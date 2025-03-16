from dal import autocomplete, forward
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import inlineformset_factory
from .models import GameType, Category, Image, Sound, Question, Hints, WhoKnowsMore, WhoKnowsMoreElement, DIFFICULTY


class CategoryForm(forms.ModelForm):
    """Form for Category model."""
    class Meta:
        model = Category
        form_tag = False
        fields = ('name_de', 'game_type', 'description_de', 'logo', 'private')


class BaseMediaForm(forms.ModelForm):
    """Base form for Image, Sound, Question, Hint, and WhoKnowsMore models."""
    class Meta:
        abstract = True
        widgets = {
            'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete'),
        }

#TODO: dynamically pass the game_type to the autocomplete view
class ImageForm(BaseMediaForm):
    """Form for Image model."""
    class Meta(BaseMediaForm.Meta):
        model = Image
        form_tag = False
        fields = ('solution', 'image_file', 'difficulty', 'explicit', 'category', 'private_new', 'author', 'license', 'file_changed')
        widgets = {**BaseMediaForm.Meta.widgets, 'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(1, 'game_type'),))}


class ImageEditForm(ImageForm):
    """Readonly version of ImageForm for editing."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['image_file', 'solution', 'author', 'license', 'file_changed']:
            self.fields[field].disabled = True


class SoundForm(BaseMediaForm):
    """Form for Sound model."""
    class Meta(BaseMediaForm.Meta):
        model = Sound
        fields = ('solution', 'sound_file', 'difficulty', 'explicit', 'category', 'private_new')
        widgets = {**BaseMediaForm.Meta.widgets, 'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(2, 'game_type'),))}


class QuestionForm(BaseMediaForm):
    """Form for Question model."""
    class Meta(BaseMediaForm.Meta):
        model = Question
        fields = ('solution', 'quiz_question', 'option1', 'option2', 'option3', 'difficulty', 'explicit', 'category', 'private_new')
        widgets = {**BaseMediaForm.Meta.widgets, 'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(4, 'game_type'),))}
        error_messages = {NON_FIELD_ERRORS: {'unique_together': "%(model_name)s's %(field_labels)s are not unique."}}


class HintForm(BaseMediaForm):
    """Form for Hints model."""
    class Meta(BaseMediaForm.Meta):
        model = Hints
        fields = ('solution', 'hint1', 'hint2', 'hint3', 'hint4', 'hint5', 'hint6', 'hint7', 'hint8', 'hint9', 'hint10', 'difficulty', 'explicit', 'category', 'private_new')
        widgets = {**BaseMediaForm.Meta.widgets, 'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(3, 'game_type'),))}


class WhoKnowsMoreForm(BaseMediaForm):
    """Form for WhoKnowsMore model."""
    class Meta(BaseMediaForm.Meta):
        model = WhoKnowsMore
        fields = ('solution', 'difficulty', 'explicit', 'category', 'private_new')
        labels = {'solution': "Frage"}
        widgets = {**BaseMediaForm.Meta.widgets, 'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(5, 'game_type'),))}


class WhoKnowsMoreElementForm(forms.ModelForm):
    """Form for WhoKnowsMoreElement model."""
    class Meta:
        model = WhoKnowsMoreElement
        form_tag = False
        fields = ('id', 'count_id', 'category_element', 'answer')
        widgets = {'count_id': forms.HiddenInput()}


WhoKnowsMoreElementFormSet = inlineformset_factory(WhoKnowsMore, WhoKnowsMoreElement, fields=['answer'], extra=10, can_delete=False, max_num=100, validate_max=True)
WhoKnowsMoreElementFormSetUpdate = inlineformset_factory(WhoKnowsMore, WhoKnowsMoreElement, fields=['answer'], extra=0, can_delete=True, max_num=100, validate_max=True)


class BaseDownloadForm(forms.ModelForm):
    """Base form for downloading models."""
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Minimale Schwierigkeit")
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Maximale Schwierigkeit")
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Ältestes Erstelldatum", required=False)
    amount = forms.IntegerField(label="Anzahl")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].initial = None
        self.fields['created_by'].required = False
        self.fields['max_difficulty'].initial = 10

    class Meta:
        abstract = True
        form_tag = False
        fields = ('explicit', 'category', 'private_new', 'created_by')
        widgets = {
            'created_by': autocomplete.ModelSelect2Multiple(url='gamefiles:user-autocomplete'),
        }
        labels = {
            'private_new': "Privates ausschließen",
            'explicit': "Anstößiges ausschließen",
            'category': "Kategorie",
            'created_by': "Ersteller",
        }


class ImageDownloadForm(BaseDownloadForm):
    """Download form for Image model."""
    class Meta(BaseDownloadForm.Meta):
        model = Image


class SoundDownloadForm(BaseDownloadForm):
    """Download form for Sound model."""
    class Meta(BaseDownloadForm.Meta):
        model = Sound


class QuestionDownloadForm(BaseDownloadForm):
    """Download form for Question model."""
    class Meta(BaseDownloadForm.Meta):
        model = Question


class HintDownloadForm(BaseDownloadForm):
    """Download form for Hints model."""
    class Meta(BaseDownloadForm.Meta):
        model = Hints


class WhoKnowsMoreDownloadForm(BaseDownloadForm):
    """Download form for WhoKnowsMore model."""
    class Meta(BaseDownloadForm.Meta):
        model = WhoKnowsMore


from django import forms
from dal import autocomplete
from .models import GameType, Category

class SolutionForm(forms.Form):
    game_type = forms.ModelChoiceField(
        queryset=GameType.objects.all(),
        label="Spielart",
        empty_label="Spielart auswählen"
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Kategorie",
        required=False,
        widget=autocomplete.ModelSelect2(
            url='gamefiles:category-autocomplete',
            forward=['game_type']  # Filters categories based on game_type
        )
    )

    category_element = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        label="Element",
        required=False,
        widget=autocomplete.ModelSelect2(
            url='gamefiles:category-element-autocomplete',
            forward=['category']  # Filters elements based on category
        )
    )

