from dal import autocomplete, forward

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import inlineformset_factory

from .models import Category, Image, Sound, Question, Hints, WhoKnowsMore, WhoKnowsMoreElement, DIFFICULTY


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        form_tag = False
        fields = ('name_de', 'game_type', 'description_de', 'logo', 'private')


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        form_tag = False
        fields = (
            'solution', 'image_file', 'difficulty', 'explicit', 'tags', 'category', 'private_new', 'author', 'license',
            'file_changed')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete',
                                                         forward=(forward.Const(2, 'game_type'),))}


class ImageEditForm(ImageForm):
    image_file = forms.ImageField(disabled=True)
    solution = forms.CharField(disabled=True)
    author = forms.CharField(disabled=True)
    license = forms.CharField(disabled=True)
    file_changed = forms.BooleanField(disabled=True)


class SoundForm(forms.ModelForm):
    class Meta:
        model = Sound
        form_tag = False
        fields = ('solution', 'sound_file', 'difficulty', 'explicit', 'tags', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete',
                                                         forward=(forward.Const(1, 'game_type'),))}


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        form_tag = False
        fields = (
            'solution', 'quiz_question', 'option1', 'option2', 'option3', 'difficulty', 'tags', 'explicit', 'category',
            'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete',
                                                         forward=(forward.Const(3, 'game_type'),))}
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }


class HintForm(forms.ModelForm):
    class Meta:
        model = Hints
        form_tag = False
        fields = ('solution', 'hint1', 'hint2', 'hint3', 'hint4', 'hint5', 'hint6', 'hint7', 'hint8', 'hint9', 'hint10',
                  'difficulty', 'tags', 'explicit', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete',
                                                         forward=(forward.Const(4, 'game_type'),))}


class WhoKnowsMoreForm(forms.ModelForm):
    class Meta:
        model = WhoKnowsMore
        form_tag = False
        fields = ('solution', 'difficulty', 'tags', 'explicit', 'category', 'private_new')
        labels = {'solution': "Frage"}
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete',
                                                         forward=(forward.Const(5, 'game_type'),))}


class WhoKnowsMoreElementForm(forms.ModelForm):
    class Meta:
        model = WhoKnowsMoreElement
        form_tag = False
        fields = ('category_element', 'answer')


WhoKnowsMoreElementFormSet = inlineformset_factory(WhoKnowsMore, WhoKnowsMoreElement, fields=['answer'], extra=10,
                                                   can_delete=False, max_num=100, validate_max=True)
WhoKnowsMoreElementFormSetUpdate = inlineformset_factory(WhoKnowsMore, WhoKnowsMoreElement, fields=['answer'], extra=0,
                                                         can_delete=True, max_num=100, validate_max=True)

class ImageDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Minimale Schwierigkeit")
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Maximale Schwierigkeit")
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Ältestes Erstelldatum", required=False)
    amount = forms.IntegerField(label="Anzahl")

    def __init__(self, *args, **kwargs):
        super(ImageDownloadForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].initial = None
        self.fields['created_by'].required = False
        self.fields['max_difficulty'].initial = 10

    class Meta:
        model = Image
        form_tag = False
        fields = ('tags', 'explicit', 'category', 'private_new', 'created_by')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'created_by': autocomplete.ModelSelect2Multiple(url='gamefiles:user-autocomplete')}
        labels = {'private_new': "Privates ausschließen",
                  'explicit': "Anstößiges ausschließen",
                  'category': "Kategorie",
                  'created_by': "Ersteller"}


class SoundDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Minimale Schwierigkeit")
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Maximale Schwierigkeit")
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Ältestes Erstelldatum", required=False)
    amount = forms.IntegerField(label="Anzahl")

    def __init__(self, *args, **kwargs):
        super(SoundDownloadForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].initial = None
        self.fields['created_by'].required = False
        self.fields['max_difficulty'].initial = 10

    class Meta:
        model = Sound
        form_tag = False
        fields = ('tags', 'explicit', 'category', 'private_new', 'created_by')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'created_by': autocomplete.ModelSelect2Multiple(url='gamefiles:user-autocomplete')}
        labels = {'private_new': "Privates ausschließen",
                  'explicit': "Anstößiges ausschließen",
                  'category': "Kategorie",
                  'created_by': "Ersteller"}


class QuestionDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Minimale Schwierigkeit")
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Maximale Schwierigkeit")
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Ältestes Erstelldatum", required=False)
    amount = forms.IntegerField(label="Anzahl")

    def __init__(self, *args, **kwargs):
        super(QuestionDownloadForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].initial = None
        self.fields['created_by'].required = False
        self.fields['max_difficulty'].initial = 10

    class Meta:
        model = Question
        form_tag = False
        fields = ('tags', 'explicit', 'category', 'private_new', 'created_by')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'created_by': autocomplete.ModelSelect2Multiple(url='gamefiles:user-autocomplete')}
        labels = {'private_new': "Privates ausschließen",
                  'explicit': "Anstößiges ausschließen",
                  'category': "Kategorie",
                  'created_by': "Ersteller"}


class HintDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Minimale Schwierigkeit")
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Maximale Schwierigkeit")
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                      label="Ältestes Erstelldatum", required=False)
    amount = forms.IntegerField(label="Anzahl")

    def __init__(self, *args, **kwargs):
        super(HintDownloadForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].initial = None
        self.fields['created_by'].required = False
        self.fields['max_difficulty'].initial = 10

    class Meta:
        model = Hints
        form_tag = False
        fields = ('tags', 'explicit', 'category', 'private_new', 'created_by')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'created_by': autocomplete.ModelSelect2Multiple(url='gamefiles:user-autocomplete')}
        labels = {'private_new': "Privates ausschließen",
                  'explicit': "Anstößiges ausschließen",
                  'category': "Kategorie",
                  'created_by': "Ersteller"}
