import django_filters
from .models import Item

from rest_framework import filters
from django.db import models  # Import the models module


class StartsWithSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)

        if not search_fields:
            return queryset

        search_terms = self.get_search_terms(request)

        if not search_terms:
            return queryset

        orm_lookups = [self.construct_search(str(search_field)) for search_field in search_fields]
        conditions = []

        for search_term in search_terms:
            queries = []
            for lookup in orm_lookups:
                queries.append(models.Q(**{lookup: search_term}))
            conditions.append(models.Q(*queries))

        queryset = queryset.filter(*conditions).distinct()
        return queryset


class ItemListFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = '__all__'