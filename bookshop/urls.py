from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'books', views.BookViewSet)
router.register(r'publishing-houses', views.PublishingViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'customers', views.UserViewSet, basename='customers')
router.register(r'comment', views.CommentAPIView)

urlpatterns = [
    path('', include(router.urls)),
    path('add-order/', views.add_ordered_books, name='add-order'),
    path('profile/', views.UserProfileViewSet.as_view(), name='profile'),
]
