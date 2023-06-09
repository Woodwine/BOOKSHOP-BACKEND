from django_filters.rest_framework import FilterSet, BaseInFilter, CharFilter, NumberFilter, NumericRangeFilter

from .models import Book


class CharFilterInFilter(BaseInFilter, CharFilter):
    pass


class BookFilter(FilterSet):
    title = CharFilterInFilter(field_name='title', lookup_expr='in')
    author_name = CharFilterInFilter(field_name='author__name', lookup_expr='in')
    author_surname = CharFilterInFilter(field_name='author__surname', lookup_expr='in')
    publishing = CharFilterInFilter(field_name='publishing__name', lookup_expr='in')
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    publication_date = NumericRangeFilter()

    class Meta:
        model = Book
        fields = ['title', 'author_name', 'author_surname', 'publishing', 'min_price', 'max_price', 'publication_date']
