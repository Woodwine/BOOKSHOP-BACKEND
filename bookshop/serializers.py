from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Book, Author, Publishing, Order, OrderedBook, Comments, DeliveryAddress


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'image', 'author', 'price']
        depth = 1


class CommentListSerializer(serializers.ModelSerializer):
    comment_author = serializers.StringRelatedField()

    class Meta:
        model = Comments
        fields = ['id', 'comment_author', 'rating', 'comment', 'date']


class BookDetailSerializer(serializers.ModelSerializer):
    book_comments = CommentListSerializer(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'image', 'author', 'publishing', 'description', 'price', 'book_comments']
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
    class Meta:
        model = OrderedBook
        fields = ['id', 'ordered_book__title', 'ordered_book__image', 'price', 'quantity']

    def create(self, validated_data):
        pass


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid', 'total_cost']
        depth = 1


class OrderDetailSerializer(serializers.ModelSerializer):
    ordered_books = OrderedBookSerializer(many=True, read_only=True)
    order_address = serializers.StringRelatedField()
    delivery_date = serializers.DateField(format='%d.%m.%Y',
                                          input_formats=['%d.%m.%Y'])

    class Meta:
        model = Order
        fields = ['id', 'ordered_book', 'customer', 'order_date', 'status', 'is_paid',
                  'delivery_date', 'shipping_cost', 'total_cost', 'order_address']


class UserSerializer(serializers.ModelSerializer):
    customer_orders = OrderListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'lsat_name', 'email', 'customer_orders']
