from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    surname = models.CharField(max_length=50, verbose_name='Фамилия')

    def __str__(self):
        return f'{self.name} {self.surname}'

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ('surname',)


class Publishing(models.Model):
    name = models.CharField(max_length=50, verbose_name='Издательство')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ('name',)


class Book(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название книги')
    image = models.ImageField(upload_to='books/', verbose_name='Фотография книги')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    publishing = models.ForeignKey(Publishing, on_delete=models.SET_NULL, null=True, verbose_name='Издательство')
    publication_date = models.PositiveSmallIntegerField(verbose_name='Год публикации')
    description = models.TextField(max_length=1000, verbose_name='Аннотация к книге')
    price = models.PositiveIntegerField(verbose_name='Цена')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ('title',)


class Order(models.Model):
    STATUS = [(1, 'Не оплачен'),
              (2, 'В работе'),
              (3, 'Передан в службу доставки'),
              (4, 'Доставлен'),
              (5, 'Отменен')]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Заказчик')
    ordered_book = models.ManyToManyField(Book, related_name='orders_books', verbose_name='Заказанные книги')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    status = models.CharField(choices=STATUS, default=1)
    total_price = models.PositiveIntegerField(verbose_name='Общая цена заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-order_date',)


class Comments(models.Model):
    RATING_CHOICES = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Название книги')
    rating = models.IntegerField(choices=RATING_CHOICES, default=0, blank=True, null=True)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария')
    comment = models.TextField(max_length=500, verbose_name='Комментарий')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        unique_together = ('book', 'comment_author')
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-date',)
