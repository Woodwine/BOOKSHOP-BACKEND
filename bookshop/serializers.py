from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, Author, Publishing, Order, OrderedBook, Comments, DeliveryAddress


class BookListSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    def get_rating(self, instance):
        return instance.rating

    def get_reviews(self, instance):
        return instance.reviews

    class Meta:
        model = Book
        fields = ['id', 'title', 'image', 'price', 'rating', 'reviews']
        depth = 1


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class CommentListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%d/%m/%y %H:%M', read_only=True)
    comment_author = serializers.StringRelatedField()

    class Meta:
        model = Comments
        fields = ['id', 'comment_author', 'rating', 'comment', 'date']


class BookDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    publishing = serializers.StringRelatedField()
    book_comments = CommentListSerializer(many=True)
    rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    def get_rating(self, instance):
        return instance.rating

    def get_reviews(self, instance):
        return instance.reviews

    class Meta:
        model = Book
        fields = ['id', 'title', 'rating', 'reviews', 'image', 'author', 'publishing', 'description', 'price',
                  'book_comments', 'publication_date', 'count_in_stock']
        depth = 1


class AuthorDetailSerializer(serializers.ModelSerializer):
    author_books = BookListSerializer(many=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'surname', 'author_books']


class PublishingDetailSerializer(serializers.ModelSerializer):
    publishing_books = BookListSerializer(many=True)

    class Meta:
        model = Publishing
        fields = ['id', 'name', 'publishing_books']


class OrderedBookSerializer(serializers.ModelSerializer):
    book_image = serializers.ImageField(source='ord_book.image')
    title = serializers.SerializerMethodField()

    class Meta:
        model = OrderedBook
        fields = ['id', 'title', 'ord_book', 'book_image', 'price', 'quantity']

    def get_title(self, instance):
        return instance.ord_book.title


class DeliveryAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryAddress
        fields = ['address', 'phone_number']


class CustomerSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin']

    def get_is_admin(self, instance):
        return instance.is_staff


class OrderListSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    order_date = serializers.DateTimeField(format='%d/%m/%y %H:%M', read_only=True)
    pay_date = serializers.DateTimeField(format='%d/%m/%y %H:%M', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'pay_date', 'status', 'is_paid', 'total_cost']


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    order_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M', read_only=True)
    ord_books = OrderedBookSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(many=True)
    delivery_date = serializers.DateTimeField(format='%d/%m/%y %H:%M')
    pay_date = serializers.DateTimeField(format='%d/%m/%y %H:%M', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid', 'pay_date', 'payment_method',
                  'delivery_date', 'shipping_cost', 'total_cost', 'delivery_address', 'ord_books']


class CustomerDetailSerializer(CustomerSerializer):
    customer_orders = OrderListSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email',  'is_admin', 'customer_orders']


class CustomerSerializerWithToken(CustomerSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email',  'is_admin', 'token']

    def get_token(self, instance):
        token = RefreshToken.for_user(instance)
        return str(token.access_token)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = CustomerSerializerWithToken(self.user).data

        for key, value in serializer.items():
            data[key] = value

        return data
