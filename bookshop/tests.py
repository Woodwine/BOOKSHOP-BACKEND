from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from .models import Order, OrderedBook, Publishing, DeliveryAddress, Book


class BookTests(APITestCase):

    def setUp(self):
        self.user_test = User.objects.create(username='User_TEST', password='dina12345')
        self.user_test_token = AccessToken.for_user(self.user_test)

        self.user_staff_test = User.objects.create(username='User_TEST_STAFF', password='dina12345', is_staff=True)
        self.user_staff_test_token = AccessToken.for_user(self.user_staff_test)

        Publishing.objects.create(name='Издательство')

        self.first_book = Book.objects.create(
            title='Book1',
            author='Author',
            publishing=Publishing.objects.get(name='Издательство'),
            publication_date='2020',
            description='It is a book',
            price=100,
            count_in_stock=100
        )

        self.data = {
            'title': 'Book2',
            'author': 'Author',
            'publishing': Publishing.objects.get(name='Издательство').pk,
            'publication_date': '2020',
            'description': 'It is a book',
            'price': 100,
            'count_in_stock': 100
        }

    """Get book list"""

    def test_get_book_list(self):
        response = self.client.get(reverse('book-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 1)

    """Get book detail"""

    def test_fail_book_detail(self):
        response = self.client.get(reverse('book-detail', kwargs={'pk': 50}))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_book_detail(self):
        response = self.client.get(reverse('book-detail', kwargs={'pk': self.first_book.id}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json().get('title'), 'Book1')

    """"Create book"""

    def test_fail_book_create(self):
        response = self.client.post(reverse('book-list'), self.data)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_user_book_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.post(reverse('book-list'), self.data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_book_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_staff_test_token))
        response = self.client.post(reverse('book-list'), self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


class OrderTests(APITestCase):

    def setUp(self):
        self.user_test = User.objects.create(username='User_TEST', password='dina12345')
        self.user_test_token = AccessToken.for_user(self.user_test)

        self.user_staff_test = User.objects.create(username='User_TEST_STAFF', password='dina12345', is_staff=True)
        self.user_staff_test_token = AccessToken.for_user(self.user_staff_test)

        Publishing.objects.create(name='Издательство')

        Book.objects.create(
            title='Book1',
            author='Author',
            publishing=Publishing.objects.get(name='Издательство'),
            publication_date='2020',
            description='It is a book',
            price=100,
            count_in_stock=100
        )

        self.first_order = Order.objects.create(
            customer=self.user_test,
        )

        self.ordered_book = OrderedBook.objects.create(
            ord_book=Book.objects.get(title='Book1'),
            quantity=1,
            price=Book.objects.get(title='Book1').price,
            order=self.first_order
        )

        self.first_address = DeliveryAddress.objects.create(
            order=self.first_order,
            address='Somewhere',
            phone_number='+12345678910'
        )

        self.data = {
            'shippingAddress': {
                'address': 'Somewhere',
                'phone_number': '+12345678910',
            },
            'orderItems': [
                {
                    'book': Book.objects.get(title='Book1').pk,
                    'quantity': 1,
                    'price': 100
                }
            ] ,
            'shippingPrice': 0,
            'totalPrice': 100,
            'paymentMethod': 'cash',
        }

    """Get order list"""

    def test_fail_order_list(self):
        response = self.client.get(reverse('order-list'))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_order_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.get(reverse('order-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_staff_order_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_staff_test_token))
        response = self.client.get(reverse('order-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    """Get order detail"""

    def test_fail_order_detail(self):
        response = self.client.get(reverse('order-detail', kwargs={'pk': self.first_order.id}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_order_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.get(reverse('order-detail', kwargs={'pk': self.first_order.id}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_staff_order_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_staff_test_token))
        response = self.client.get(reverse('order-detail', kwargs={'pk': self.first_order.id}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    """Create order"""

    def test_fail_order_create(self):
        response = self.client.post(reverse('add-order'), self.data)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_order_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.post(reverse('add-order'), self.data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class UserTests(APITestCase):

    def setUp(self):
        self.user_test = User.objects.create(username='User_TEST', password='dina12345')
        self.user_test_token = AccessToken.for_user(self.user_test)

        self.user_staff_test = User.objects.create(username='User_TEST_STAFF', password='dina12345', is_staff=True)
        self.user_staff_test_token = AccessToken.for_user(self.user_staff_test)

        self.data = {'username': 'User_TEST_NEW'}

    """Get list of users"""

    def test_fail_users_list(self):
        response = self.client.get(reverse('users-list'))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_stuff_users_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.get(reverse('users-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 1)

    def test_stuff_users_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_staff_test_token))
        response = self.client.get(reverse('users-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    """Get user details"""

    def test_fail_user_detail(self):
        response = self.client.get(reverse('users-detail', kwargs={'pk': self.user_test.id}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_own_user_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.get(reverse('users-detail', kwargs={'pk': self.user_test.id}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_staff_user_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_staff_test_token))
        response = self.client.get(reverse('users-detail', kwargs={'pk': self.user_test.id}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    """Change user details"""

    def test_fail_change_user_detail(self):
        response = self.client.patch(reverse('users-detail', kwargs={'pk': self.user_test.id}), self.data)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_user_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_test_token))
        response = self.client.patch(reverse('users-detail', kwargs={'pk': self.user_test.id}), self.data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class PublishingTests(APITestCase):

    def setUp(self):
        self.user_test = User.objects.create(username='User_TEST', password='dina12345')
        self.user_test_token = AccessToken.for_user(self.user_test)

        self.user_staff_test = User.objects.create(username='User_TEST_STAFF', password='dina12345', is_staff=True)
        self.user_staff_test_token = AccessToken.for_user(self.user_staff_test)

        self.first_publishing = Publishing.objects.create(name='Издательство1')

        self.data = {'name': 'Издательство2'}

    """Get publishing list"""

    def test_get_publishing_list(self):
        response = self.client.get(reverse('publishing-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 1)

    """Get publishing detail"""

    def test_fail_publishing_detail(self):
        response = self.client.get(reverse('publishing-detail', kwargs={'pk': 50}))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_publishing_detail(self):
        response = self.client.get(reverse('publishing-detail', kwargs={'pk': self.first_publishing.id}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json().get('name'), 'Издательство1')

    """Create publishing"""

    def test_fail_publishing_create(self):
        response = self.client.post(reverse('publishing-list'), self.data)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_publishing_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.user_staff_test_token))
        response = self.client.post(reverse('publishing-list'), self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


