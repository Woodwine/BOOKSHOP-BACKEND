from django.contrib import admin

from .models import Author, Publishing, Book, Order, Comments, DeliveryAddress, OrderedBook


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['surname']


@admin.register(Publishing)
class PublishingAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publishing', 'publication_date', 'price', 'count_in_stock']
    search_fields = ['title', 'publishing__name', 'author__name', 'author__surname']
    list_filter = ['publishing__name', 'publication_date']


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['order', 'address', 'phone_number']
    search_fields = ['order']


@admin.register(OrderedBook)
class OrderedBookAdmin(admin.ModelAdmin):
    list_display = ['order', 'ord_book', 'quantity', 'price']
    search_fields = ['order', 'ord_book']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order_date', 'status', 'is_paid', 'shipping_cost', 'total_cost']
    search_fields = ['customer', 'status']
    list_filter = ['status']


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['comment_author', 'rating', 'book', 'date']
    search_fields = ['comment_author__user', 'recipe__name']