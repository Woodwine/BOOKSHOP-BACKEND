from django.contrib.auth.models import User
from rest_framework import generics, viewsets, mixins, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .models import Book, Publishing, Author, Order, DeliveryAddress, OrderedBook
from .serializers import PublishingDetailSerializer, AuthorDetailSerializer, BookListSerializer, BookDetailSerializer, \
    OrderDetailSerializer, OrderListSerializer, UserSerializer
from .permissions import IsAdminUserOrReadOnly, IsOwner
from .service import BookFilter


class PublishingViewSet(ModelViewSet):
    queryset = Publishing.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = PublishingDetailSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = AuthorDetailSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'surname']


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['price', 'publication_date']
    search_fields = ['title', 'author__surname', 'publishing__name']
    filterset_class = BookFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        if self.action == 'retrieve':
            return BookDetailSerializer


class OrderViewSet(ModelViewSet):
    permission_classes = (IsAdminUserOrReadOnly,)
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
@permission_classes(['IsAuthenticated'])
def add_ordered_books(request):
    user = request.user
    data = request.data

    ordered_books = data['ordered_books']
    if ordered_books and len(ordered_books) == 0:
        return Response({'detail': 'Товар не выбран'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        customer=user,
        shipping_cost=data['shipping_cost'],
        total_cost=data['total_cost']
    )

    order_address = DeliveryAddress.objects.create(
        order=order,
        address=data['order_address'],
        phone_number=data['phone_number']
    )
    for item in ordered_books:
        book = Book.objects.get(id=item['book'])
        new_ord_book = OrderedBook.objects.create(
            ord_book=book,
            name=book.title,
            image=book.image.url,
            quantity=item['quantity'],
            price=item['price'],
            order=order,
        )
        book.count_in_stock -= new_ord_book.quantity
        book.save()
    serializer = OrderDetailSerializer(order, many=True)
    return Response(serializer.data)


class UserViewSet(ModelViewSet):
    permission_classes = (IsOwner, )
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['username', 'last_name']

    def get_queryset(self):
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            return User.objects.get(id=self.request.user.id)
        if self.request.user.is_staff:
            return User.objects.all()

