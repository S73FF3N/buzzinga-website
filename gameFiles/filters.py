import django_filters
from django import forms
from dal import autocomplete
from .models import Image, Sound, Question, Category, Hints, WhoKnowsMore, QuizGameResult


class BaseFilter(django_filters.FilterSet):
    """Mixin to define common filter fields for multiple models."""
    solution = django_filters.CharFilter(lookup_expr='icontains', label="Lösung")
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='gamefiles:category-autocomplete'),
        label="Kategorie"
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
            {"Meta": type("Meta", (), {"model": model, "fields": ['solution', 'category', 'private_new'], "order_by": ['pk']})}
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


class QuizGameResultFilter(django_filters.FilterSet):
    # Optional: range filter for dates
    quiz_date__gte = django_filters.DateFilter(
        field_name="quiz_date", lookup_expr="gte", label="Datum (von)", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    quiz_date__lte = django_filters.DateFilter(
        field_name="quiz_date", lookup_expr="lte", label="Datum (bis)", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = QuizGameResult
        fields = ["game_type", "quiz_group", "quizmaster"]
        labels = {
            "game_type": "Spieltyp",
            "quiz_group": "Quizgruppe",
            "quizmaster": "Quizmaster",
        }
