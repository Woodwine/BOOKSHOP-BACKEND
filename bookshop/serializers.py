from rest_framework import serializers

from .models import Book, Author, Publishing, Order


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'image', 'price']


class BookDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    publishing = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['title', 'image', 'author', 'publishing', 'description', 'price']


class AuthorSerializer(serializers.ModelSerializer):
    books_author = serializers.StringRelatedField(many=True)

    class Meta:
        model = Author
        fields = ['name', 'surname', 'books_author']


class PublishingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publishing
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        depth = 1
