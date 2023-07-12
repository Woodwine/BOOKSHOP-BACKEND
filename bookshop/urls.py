from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'publishing-houses', views.PublishingViewSet)
# router.register(r'authors', views.AuthorViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'users', views.UserProfileViewSet, basename='users')
router.register(r'comment', views.CommentAPIView)
# router.register(r'profile', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('add-order/', views.add_ordered_books, name='add-order'),
    path('pay/<str:pk>/', views.update_order_to_pay, name='pay-order'),
    path('upload_image/', views.upload_image, name='upload-image'),
]
