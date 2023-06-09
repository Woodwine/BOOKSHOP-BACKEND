from rest_framework import generics, viewsets, mixins, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Book, Publishing, Author
from .serializers import PublishingSerializer, AuthorSerializer, BookListSerializer, BookDetailSerializer
from .permissions import IsAdminUserOrReadOnly
from .service import BookFilter


class PublishingViewSet(ReadOnlyModelViewSet):
    queryset = Publishing.objects.all()
    serializer_class = PublishingSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']


class AuthorViewSet(ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'surname']


class BookViewSet(ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['price', 'publication_date']
    search_fields = ['title', 'author__surname', 'publishing__name']
    filterset_class = BookFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        if self.action == 'retrieve':
            return BookDetailSerializer



