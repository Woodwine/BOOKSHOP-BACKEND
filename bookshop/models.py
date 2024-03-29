from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator


class InStockManager(models.Manager):
    """
    Returns a queryset of books in stock.
    """

    def get_queryset(self):
        return super().get_queryset().filter(count_in_stock__gt=0)


class Publishing(models.Model):
    """
    Represents a publishing consisting publishing name
    """

    name = models.CharField(max_length=50, verbose_name='Издательство')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ('name',)


class Book(models.Model):
    """
    Represents a book consisting book title, book image, book author, publishing, publication date,
    description, book price, number of books in stock
    """

    title = models.CharField(max_length=150, verbose_name='Название книги')
    image = models.ImageField(upload_to='books/', default='/media/books/default.jpg', verbose_name='Фотография книги')
    author = models.CharField(default='', null=True, verbose_name='Автор')
    publishing = models.ForeignKey(Publishing, related_name='publishing_books',
                                   on_delete=models.PROTECT, verbose_name='Издательство')
    publication_date = models.PositiveSmallIntegerField(validators=[MinValueValidator(1990)],
                                                        verbose_name='Год публикации')
    description = models.TextField(max_length=1000, verbose_name='Аннотация к книге')
    price = models.DecimalField(max_digits=7, default=0, decimal_places=2, verbose_name='Цена')
    count_in_stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    objects = models.Manager()
    in_stock_objects = InStockManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'


class Order(models.Model):
    """
    Represents an order consisting customer, order date, status of order, payment method, status of payment,
    payment date, delivery date, shipping cost, total cost of the order.
    """

    STATUS = [('В работе', 'В работе'),
              ('Передан в службу доставки', 'Передан в службу доставки'),
              ('Доставлен', 'Доставлен'),
              ('Отменен', 'Отменен')]

    customer = models.ForeignKey(User, related_name='customer_orders', on_delete=models.CASCADE,
                                 verbose_name='Заказчик')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    status = models.CharField(choices=STATUS, default='В работе', verbose_name='Статус заказа')
    is_paid = models.BooleanField(default=False, verbose_name='Статус оплаты')
    pay_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')
    delivery_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата доставки')
    shipping_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Цена доставки')
    total_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Цена заказа с учетом доставки')
    payment_method = models.CharField(default='Card', verbose_name='Способ оплаты')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-order_date',)

    def __str__(self):
        return f'Заказ {self.pk}'


class OrderedBook(models.Model):
    """
    Represents the book added to the order consisting ordered book, quantity of books, book price, order
    """

    ord_book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='ordered_books')
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Цена')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='ord_books',
                              verbose_name='Номер заказа')

    class Meta:
        verbose_name = 'Заказанная книга'
        verbose_name_plural = 'Заказанные книги'
        ordering = ('-order',)

    def __str__(self):
        return self.ord_book.title


class DeliveryAddress(models.Model):
    """
    Represents a delivery address consisting order, address, phone number of customer
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_address', verbose_name='Номер заказа')
    address = models.TextField(max_length=250, verbose_name='Адрес заказа')
    phone_number_regex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators=[phone_number_regex], blank=True, max_length=16, verbose_name='Номер телефона')

    def __str__(self):
        return f'{self.address}, {self.phone_number}'

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'
        ordering = ('-order',)


class Comments(models.Model):
    """
    Represents a user comment consisting commented book, book rating, comment author, comment, date of comment
    """

    RATING_CHOICES = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]

    book = models.ForeignKey(Book, related_name='book_comments', on_delete=models.CASCADE,
                             verbose_name='Название книги')
    rating = models.IntegerField(choices=RATING_CHOICES, default=0, blank=True, null=True, verbose_name='Рейтинг')
    comment_author = models.ForeignKey(User, related_name='comment_author',
                                       on_delete=models.CASCADE, verbose_name='Автор комментария')
    comment = models.TextField(max_length=500, verbose_name='Комментарий')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        unique_together = ('book', 'comment_author')
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-date',)

    def __str__(self):
        return f'Комментарий {self.comment_author}'

