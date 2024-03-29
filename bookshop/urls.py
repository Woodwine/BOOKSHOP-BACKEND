from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'publishing-houses', views.PublishingViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'comment', views.CommentAPIView)

urlpatterns = [
    path('', include(router.urls)),
    path('add-order/', views.add_ordered_books, name='add-order'),
    path('pay/<str:pk>/', views.update_order_to_pay, name='pay-order'),
    path('upload_image/', views.upload_image, name='upload-image'),
    path('order_status/<str:pk>/', views.update_order_status, name='update-order-status'),
]
