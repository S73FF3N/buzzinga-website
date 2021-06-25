import django_filters
from dal import autocomplete

from .models import Tag, CategoryElement, Category

class ProfileFilter(django_filters.FilterSet):
    solution = django_filters.CharFilter(lookup_expr='icontains', label="Lösung")
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.filter(private=False), widget=autocomplete.ModelSelect2Multiple(url='gamefiles:category-autocomplete'), label="Kategorie")
    tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), widget=autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'))
    private_new = django_filters.BooleanFilter(label='Privat')

    class Meta:
        model = CategoryElement
        fields = ['solution', 'category', 'private_new', 'tags']
        order_by = ['pk']

class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = ['private']
        order_by = ['pk']