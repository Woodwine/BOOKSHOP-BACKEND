from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from rest_framework import filters, status, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from datetime import datetime

from .models import Book, Publishing, Order, DeliveryAddress, OrderedBook, Comments
from .serializers import PublishingDetailSerializer, BookListSerializer, BookDetailSerializer, \
    OrderDetailSerializer, OrderListSerializer, CommentCreateSerializer, MyTokenObtainPairSerializer, \
    CustomerDetailSerializer, \
    CustomerSerializer, CustomerSerializerWithToken, BookCreateSerializer
from .permissions import IsAdminUserOrReadOnly, IsOwner, IsOrderOwner, IsCommentOwner
from .service import BookFilter
from rest_framework_simplejwt.views import TokenObtainPairView


class PublishingViewSet(ModelViewSet):
    """
    Represents a publishing house
    """

    queryset = Publishing.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = PublishingDetailSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']


class BookViewSet(ModelViewSet):
    """
    Represents list of all books in stock or one book only. Be used also for creating and updating the book by staff.
    """

    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title']
    filterset_class = BookFilter

    def get_serializer_class(self):
        if self.action in ['list']:
            return BookListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookCreateSerializer
        else:
            return BookDetailSerializer

    def get_queryset(self):
        query = self.request.query_params.get('keyword')
        if query is None:
            query = ''
        if self.request.user.is_staff:
            return Book.objects.filter(Q(title__icontains=query.lower()) |
                                       Q(title__icontains=query.upper()) |
                                       Q(title__icontains=query.capitalize()))
        else:
            return Book.in_stock_objects.filter(Q(title__icontains=query.lower()) |
                                                Q(title__icontains=query.upper()) |
                                                Q(title__icontains=query.capitalize())).annotate(
                rating=Avg('book_comments__rating')).annotate(
                reviews=Count('book_comments__comment'))


@api_view(['POST'])
def upload_image(request):
    """
    Uploads an image to the book item
    """
    data = request.data
    book_id = data['book_id']
    book = Book.objects.get(id=book_id)
    book.image = request.FILES.get('image')
    book.save()
    return Response('Фотография загружена')


class OrderViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """
    Represents list of all customer orders or one order. Be used also for updating the order by staff.
    """

    permission_classes = (IsOrderOwner,)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['order_date', 'is_paid', 'status', 'total_cost']
    search_fields = ['customer__surname', 'status']

    def get_queryset(self):
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            return Order.objects.filter(customer=self.request.user)
        if self.request.user.is_staff:
            return Order.objects.all()

    def get_serializer_class(self):
        if self.action in ['list']:
            return OrderListSerializer
        else:
            return OrderDetailSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_ordered_books(request):
    """
    Creates a new order, adds delivery address and ordered books
    """
    user = request.user
    data = request.data
    shipping_address = data['shippingAddress']
    ordered_books = data['orderItems']

    if ordered_books and len(ordered_books) == 0:
        return Response({'detail': 'Товар не выбран'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        customer=user,
        shipping_cost=data['shippingPrice'],
        total_cost=data['totalPrice'],
        payment_method=data['paymentMethod']
    )

    DeliveryAddress.objects.create(
        order=order,
        address=shipping_address['address'],
        phone_number=shipping_address['phone_number'],
    )

    for item in ordered_books:
        book = Book.objects.get(id=item['book'])
        new_ord_book = OrderedBook.objects.create(
            ord_book=book,
            quantity=item['quantity'],
            price=item['price'],
            order=order,
        )
        book.count_in_stock -= new_ord_book.quantity
        book.save()

    serializer = OrderDetailSerializer(order)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsOrderOwner])
def update_order_to_pay(request, pk):
    """
    Updates payment status of the order by order owner
    """

    order = Order.objects.get(pk=pk)

    order.is_paid = True
    order.pay_date = datetime.now()
    order.save()
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_order_status(request, pk):
    """
    Updates order status of the order by staff
    """

    data = request.data
    order = Order.objects.get(pk=pk)

    order.status = data
    if order.status == 'Доставлен':
        order.delivery_date = datetime.now()
    order.save()
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data)


class CommentAPIView(mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, GenericViewSet):
    """
    Represents list of all book comments or only one comment.
    Be used also for creating, updating and deleting the comment
    """

    permission_classes = [IsCommentOwner]
    serializer_class = CommentCreateSerializer
    queryset = Comments.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        data['comment_author'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserProfileViewSet(ModelViewSet):
    """
    Represents list of all users or information about one user.
    Be used also for updating user information by owner or staff
    """

    permission_classes = (IsOwner,)
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['username']

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        elif self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerSerializerWithToken
        elif self.request.user.is_authenticated:
            return CustomerDetailSerializer

