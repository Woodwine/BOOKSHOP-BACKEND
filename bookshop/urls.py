from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'books', views.BookViewSet)
router.register(r'publishing-houses', views.PublishingViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('add-order/', views.add_ordered_books, name='add-order'),
]
