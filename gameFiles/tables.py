import django_tables2 as dt2
from .models import Category, Sound, Image, Question, Hints, WhoKnowsMore


def print_checkbox_pk(**kwargs):
    """Generates an ID for checkboxes based on the record's primary key."""
    pk = kwargs.get("record")
    return f"checkbox_{pk.pk}" if pk else "checkbox_0"


class BaseTable(dt2.Table):
    """Base table class with common columns and attributes."""
    
    select = dt2.CheckBoxColumn(
        accessor="pk",
        attrs={
            "th__input": {"onclick": "toggle(this)"},
            "input": {"class": "select_checkbox", "id": print_checkbox_pk, "type": "checkbox"},
        },
        orderable=False
    )

    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")
    delete = dt2.TemplateColumn(template_name='delete_column.html', verbose_name="Löschen")
    solution = dt2.Column(verbose_name="Lösung")
    category = dt2.Column(verbose_name="Kategorie")
    difficulty = dt2.Column(verbose_name="Schwierigkeit")
    private_new = dt2.BooleanColumn(verbose_name="Privat")

    class Meta:
        abstract = True  # Prevents Django from treating this as a standalone table
        per_page = 10
        attrs = {"class": "table table-nice table-hover", "style": "table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."


class SoundTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Sound
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit', 'delete', 'select')


class ImageTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Image
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit', 'delete', 'select')


class QuestionTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Question
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit', 'delete', 'select')


class HintTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Hints
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit', 'delete', 'select')


class WhoKnowsMoreTable(BaseTable):
    solution = dt2.Column(verbose_name="Frage")  # Overrides base solution label

    class Meta(BaseTable.Meta):
        model = WhoKnowsMore
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit', 'delete', 'select')


class CategoryTable(dt2.Table):
    """Category table with custom edit and delete columns."""
    
    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")
    delete = dt2.TemplateColumn(template_name='delete_column.html', verbose_name="Löschen")

    class Meta:
        model = Category
        fields = ('name_de', 'game_type', 'private', 'edit', 'delete')
        per_page = 10
        attrs = {"class": "table table-nice table-hover", "style": "table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."
