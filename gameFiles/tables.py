import django_tables2 as dt2

from .models import Category, Sound, Image, Question, Hints

def print_checkbox_pk(**kwargs):
    pk = kwargs.get("record", None)
    if pk is None:
        return "checkbox_0"
    else:
        return "checkbox_"+str(pk.pk)

class SoundTable(dt2.Table):
    select = dt2.CheckBoxColumn(accessor="pk", attrs = { "th__input":
                                        {"onclick": "toggle(this)"}, "input":{"class":"select_checkbox", "id":print_checkbox_pk, "type":"checkbox"}},
                                        orderable=False)#dt2.TemplateColumn(template_name='select_column.html', orderable=False)
    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")
    solution = dt2.Column(verbose_name="Lösung")
    category = dt2.Column(verbose_name="Kategorie")
    difficulty = dt2.Column(verbose_name="Schwierigkeit")
    private_new = dt2.BooleanColumn(verbose_name="Privat")

    class Meta:
        model = Sound
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit')
        per_page = 10
        attrs = {"class":"table table-hover", "style":"table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."

class ImageTable(dt2.Table):
    select = dt2.CheckBoxColumn(accessor="pk", attrs = { "th__input":
                                        {"onclick": "toggle(this)"}, "input":{"class":"select_checkbox", "id":print_checkbox_pk, "type":"checkbox"}},
                                        orderable=False)#dt2.TemplateColumn(template_name='select_column.html', orderable=False)
    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")
    solution = dt2.Column(verbose_name="Lösung")
    category = dt2.Column(verbose_name="Kategorie")
    difficulty = dt2.Column(verbose_name="Schwierigkeit")
    private_new = dt2.BooleanColumn(verbose_name="Privat")

    class Meta:
        model = Image
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit')
        per_page = 10
        attrs = {"class":"table table-hover", "style":"table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."

class QuestionTable(dt2.Table):
    select = dt2.CheckBoxColumn(accessor="pk", attrs = { "th__input":
                                        {"onclick": "toggle(this)"}, "input":{"class":"select_checkbox", "id":print_checkbox_pk, "type":"checkbox"}},
                                        orderable=False)#dt2.TemplateColumn(template_name='select_column.html', orderable=False)
    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")
    solution = dt2.Column(verbose_name="Lösung")
    category = dt2.Column(verbose_name="Kategorie")
    difficulty = dt2.Column(verbose_name="Schwierigkeit")
    private_new = dt2.BooleanColumn(verbose_name="Privat")

    class Meta:
        model = Question
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit')
        per_page = 10
        attrs = {"class":"table table-hover", "style":"table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."

class HintTable(dt2.Table):
    select = dt2.CheckBoxColumn(accessor="pk", attrs = { "th__input":
                                        {"onclick": "toggle(this)"}, "input":{"class":"select_checkbox", "id":print_checkbox_pk, "type":"checkbox"}},
                                        orderable=False)#dt2.TemplateColumn(template_name='select_column.html', orderable=False)
    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")
    solution = dt2.Column(verbose_name="Lösung")
    category = dt2.Column(verbose_name="Kategorie")
    difficulty = dt2.Column(verbose_name="Schwierigkeit")
    private_new = dt2.BooleanColumn(verbose_name="Privat")

    class Meta:
        model = Hints
        fields = ('solution', 'category', 'difficulty', 'private_new', 'edit')
        per_page = 10
        attrs = {"class":"table table-hover", "style":"table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."

class CategoryTable(dt2.Table):
    edit = dt2.TemplateColumn(template_name='edit_column.html', verbose_name="Ändern")

    class Meta:
        model = Category
        fields = ('name_de', 'game_type', 'private', 'edit')
        per_page = 10
        attrs = {"class": "table table-hover", "style": "table-layout: fixed;"}
        template_name = "profile_table.html"
        empty_text = "There is no data matching the search criteria..."