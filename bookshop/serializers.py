from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Book, Author, Publishing, Order, OrderedBook, Comments


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'image', 'price']
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
        fields = ['comment_author', 'rating', 'comment', 'date']


class BookDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    publishing = serializers.StringRelatedField()
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
    book_image = serializers.ImageField(source='ord_book.image')

    class Meta:
        model = OrderedBook
        fields = ['id', 'ord_book', 'book_image', 'price', 'quantity']


class OrderListSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format='%d/%m/%y %H:%M', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid', 'total_cost']


class OrderDetailSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M', read_only=True)
    ord_books = OrderedBookSerializer(many=True, read_only=True)
    delivery_address = serializers.StringRelatedField(many=True, read_only=True)
    delivery_date = serializers.DateTimeField(format='%d/%m/%y %H:%M')

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid',
                  'delivery_date', 'shipping_cost', 'total_cost', 'delivery_address', 'ord_books']


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CustomerDetailSerializer(serializers.ModelSerializer):
    customer_orders = OrderListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'customer_orders']
