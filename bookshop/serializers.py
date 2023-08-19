from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, Publishing, Order, OrderedBook, Comments, DeliveryAddress


class BookListSerializer(serializers.ModelSerializer):
    """
    Returns list of books consisting book id, book title, book image, book price, average rating, number of reviews
    """

    rating = serializers.SerializerMethodField(read_only=True, required=None)
    reviews = serializers.SerializerMethodField(read_only=True, required=None)

    def get_rating(self, instance):
        return instance.rating

    def get_reviews(self, instance):
        return instance.reviews

    class Meta:
        model = Book
        fields = ['id', 'title', 'image', 'price', 'rating', 'reviews']


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Returns information about the created book consisting id, title, image, publishing, publication date, description,
    number of books in stock, book price
    """

    class Meta:
        model = Book
        fields = ['id', 'title', 'image', 'author', 'publishing', 'publication_date', 'description',
                  'count_in_stock', 'price']


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Returns information about the created comment consisting id, commented book, book rating, comment author, comment, date of comment
    """

    class Meta:
        model = Comments
        fields = '__all__'


class CommentListSerializer(serializers.ModelSerializer):
    """
    Returns list of comments consisting id, comment author, book rating, comment, date of comment
    """

    date = serializers.DateTimeField(format='%d/%m/%y %H:%M', read_only=True)
    comment_author = serializers.StringRelatedField()

    class Meta:
        model = Comments
        fields = ['id', 'comment_author', 'rating', 'comment', 'date']


class PublishingDetailSerializer(serializers.ModelSerializer):
    """
    Returns list of publishing houses consisting id, publishing name
    """

    class Meta:
        model = Publishing
        fields = ['id', 'name']


class BookDetailSerializer(serializers.ModelSerializer):
    """
    Returns information about the book consisting id, book title, image, author, publishing, description, book price,
    publication date, average rating, number of reviews, book comments, number of books in stock
    """

    publishing = PublishingDetailSerializer()
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


class OrderedBookSerializer(serializers.ModelSerializer):
    """
    Returns list of ordered books consisting ordered book id, book, book title, image, price, quantity of books
    """

    book_image = serializers.ImageField(source='ord_book.image')
    title = serializers.SerializerMethodField()

    class Meta:
        model = OrderedBook
        fields = ['id', 'title', 'ord_book', 'book_image', 'price', 'quantity']

    def get_title(self, instance):
        return instance.ord_book.title


class DeliveryAddressSerializer(serializers.ModelSerializer):
    """
    Returns information about delivery address consisting address and customer phone number
    """

    class Meta:
        model = DeliveryAddress
        fields = ['address', 'phone_number']


class CustomerSerializer(serializers.ModelSerializer):
    """
    Returns list of customers consisting user id, username, email, staff status
    """

    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin']

    def get_is_admin(self, instance):
        return instance.is_staff


class OrderListSerializer(serializers.ModelSerializer):
    """
    Returns list of orders consisting order id, customer, order date, payment date, order status,
    payment status, total cost of the order
    """

    customer = CustomerSerializer()
    order_date = serializers.DateTimeField(format='%d/%m/%y', read_only=True)
    pay_date = serializers.DateTimeField(format='%d/%m/%y', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'pay_date', 'status', 'is_paid', 'total_cost']


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Returns information about the order consisting order id, customer, order date, order status, payment status,
    payment date, payment method, delivery date, shipping cost, total cost of the order, delivery address,
    ordered books
    """

    customer = CustomerSerializer()
    order_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M', read_only=True)
    ord_books = OrderedBookSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(many=True)
    delivery_date = serializers.DateTimeField(format='%d/%m/%y')
    pay_date = serializers.DateTimeField(format='%d/%m/%y', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid', 'pay_date', 'payment_method',
                  'delivery_date', 'shipping_cost', 'total_cost', 'delivery_address', 'ord_books']


class CustomerSerializerWithToken(CustomerSerializer):
    """
    Returns information about the customer consisting customer id, username, email, staff status, JWT token
    """

    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email',  'is_admin', 'token']

    def get_token(self, instance):
        token = RefreshToken.for_user(instance)
        return str(token.access_token)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Validates token pair
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = CustomerSerializerWithToken(self.user).data

        for key, value in serializer.items():
            data[key] = value

        return data
