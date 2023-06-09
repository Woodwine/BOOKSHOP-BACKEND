from django.contrib import admin

# Register your models here.
from .models import Author, Publishing, Book, Order, Comments


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['surname']


@admin.register(Publishing)
class PublishingAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publishing', 'publication_date', 'price']
    search_fields = ['title', 'publishing__name', 'author__name', 'author__surname']
    list_filter = ['publishing__name', 'author__surname', 'publication_date']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ['customer__name', 'ordered_book__title', 'status']
    list_filter = ['status']


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['comment_author', 'rating', 'book', 'date']
    search_fields = ['comment_author__user', 'recipe__name']