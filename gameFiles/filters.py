import django_filters
from dal import autocomplete
from .models import Tag, Image, Sound, Question, Category, Hints, WhoKnowsMore


class BaseFilter(django_filters.FilterSet):
    """Mixin to define common filter fields for multiple models."""
    solution = django_filters.CharFilter(lookup_expr='icontains', label="Lösung")
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='gamefiles:category-autocomplete'),
        label="Kategorie"
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete')
    )
    private_new = django_filters.BooleanFilter(label='Privat')

    class Meta:
        abstract = True


class BaseProfileFilter(BaseFilter):
    """Base filter for Image, Sound, Question, Hints, and WhoKnowsMore models."""
    
    @classmethod
    def create_filter(cls, model):
        """Dynamically creates a filter class for the given model."""
        return type(
            f"{model.__name__}Filter",
            (cls,),
            {"Meta": type("Meta", (), {"model": model, "fields": ['solution', 'category', 'private_new', 'tags'], "order_by": ['pk']})}
        )


# Generate filter classes dynamically
ImageFilter = BaseProfileFilter.create_filter(Image)
SoundFilter = BaseProfileFilter.create_filter(Sound)
QuestionFilter = BaseProfileFilter.create_filter(Question)
HintFilter = BaseProfileFilter.create_filter(Hints)
WhoKnowsMoreFilter = BaseProfileFilter.create_filter(WhoKnowsMore)


class CategoryFilter(django_filters.FilterSet):
    """Filter for Category model."""
    class Meta:
        model = Category
        fields = ['private']
        order_by = ['pk']
