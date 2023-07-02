from django.contrib.auth.models import User
from django.db.models import Avg, Count
from rest_framework import filters, status, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.contrib.auth.hashers import make_password

from .models import Book, Publishing, Author, Order, DeliveryAddress, OrderedBook, Comments
from .serializers import PublishingDetailSerializer, AuthorDetailSerializer, BookListSerializer, BookDetailSerializer, \
    OrderDetailSerializer, OrderListSerializer, CommentCreateSerializer, MyTokenObtainPairSerializer, CustomerDetailSerializer, \
    CustomerSerializer
from .permissions import IsAdminUserOrReadOnly, IsOwner, IsOrderOwner, IsCommentOwner
from .service import BookFilter
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class PublishingViewSet(ModelViewSet):
    """
    Presentation of publishing houses and the books they have published.
    """
    queryset = Publishing.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = PublishingDetailSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']


class AuthorViewSet(ModelViewSet):
    """
    Presentation of writers and the books they have written.
    """
    queryset = Author.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = AuthorDetailSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'surname']


class BookViewSet(ModelViewSet):
    """
    Presentation of all the books that are available.
    """
    queryset = Book.in_stock_objects.all().annotate(rating=Avg('book_comments__rating')).annotate(
        reviews=Count('book_comments__comment'))
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['price', 'publication_date']
    search_fields = ['title', 'author__surname', 'publishing__name']
    filterset_class = BookFilter

    def get_serializer_class(self):
        if self.action in ['list', 'post']:
            return BookListSerializer
        else:
            return BookDetailSerializer


class OrderViewSet(ModelViewSet):
    """
    Presentation of all customer orders.
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


def get_costs(total_cost):
    """
    Calculation of the delivery cost and the total cost of the order.
    """
    shipping_cost = 0
    if total_cost <= 2000:
        shipping_cost = 300
        total_cost += shipping_cost
    return shipping_cost, total_cost


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_ordered_books(request):
    """
    Adding a new order.
    """
    user = request.user
    data = request.data

    ordered_books = data['ordered_books']
    if ordered_books and len(ordered_books) == 0:
        return Response({'detail': 'Товар не выбран'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        customer=user
    )
    DeliveryAddress.objects.create(
        order=order,
        address=data['delivery_address'],
        phone_number=data['phone_number']
    )

    cost = 0

    for item in ordered_books:
        book = Book.objects.get(id=item['book'])
        new_ord_book = OrderedBook.objects.create(
            ord_book=book,
            quantity=item['quantity'],
            price=book.price,
            order=order,
        )
        cost += new_ord_book.price * new_ord_book.quantity
        book.count_in_stock -= new_ord_book.quantity
        book.save()

    order.shipping_cost, order.total_cost = get_costs(cost)
    order.save()
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data)


class CommentAPIView(mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, GenericViewSet):
    """
    Creating, updating and deleting user comments.
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


class UserViewSet(ModelViewSet):
    """
    Getting user information for staff.
    """
    permission_classes = (IsAdminUser,)
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['username', 'last_name']
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerSerializer
        else:
            return CustomerDetailSerializer


class UserProfileViewSet(RetrieveUpdateAPIView):
    """
    Getting user information.
    """
    permission_classes = (IsOwner,)
    serializer_class = CustomerDetailSerializer

    def get_object(self):
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            return User.objects.get(id=self.request.user.id)

#
# @api_view(['POST'])
# def register_user(request):
#     data = request.data
#
#     user = User.objects.create_user(
#         username=data['username'],
#         first_name=data['first_name'],
#         last_name=data['last_name'],
#         email=data['email'],
#         password=make_password(data['password'])
#     )
#
#     serializer = UserSerializerWithToken(user, many=False)
#
#     return Response(serializer.data)
