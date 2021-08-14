from dal import autocomplete, forward

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from .models import Tag, Category, Image, Sound, Question, DIFFICULTY

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        form_tag = False
        fields = ('name_de', 'game_type', 'description_de', 'logo', 'private')
        labels = {
            "name_de": "Name",
            "description_de": "Beschreibung",
            "game_type": "Spieltyp",
            "private": "Privat"
        }

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        form_tag = False
        fields = ('solution', 'image_file', 'difficulty', 'explicit', 'tags', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(1, 'game_type'),))}
        labels = {
            "name_de": "Name",
            "description_de": "Beschreibung",
            "game_type": "Spieltyp",
            "private_new": "Privat",
            "category": "Kategorie",
            "solution": "Lösung",
            "difficulty": "Schwierigkeit",
            "explicit": "explizit",
            "image_file": "Bilddatei"
        }

class SoundForm(forms.ModelForm):
    class Meta:
        model = Sound
        form_tag = False
        fields = ('solution', 'sound_file', 'difficulty', 'explicit', 'tags', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(2, 'game_type'),))}
        labels = {
            "name_de": "Name",
            "description_de": "Beschreibung",
            "game_type": "Spieltyp",
            "private_new": "Privat",
            "category": "Kategorie",
            "solution": "Lösung",
            "difficulty": "Schwierigkeit",
            "explicit": "explizit",
            "sound_file": "Sounddatei"
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        form_tag = False
        fields = ('solution', 'quiz_question', 'option1', 'option2', 'option3', 'difficulty', 'tags', 'explicit', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(3, 'game_type'),))}
        labels = {
            "name_de": "Name",
            "description_de": "Beschreibung",
            "game_type": "Spieltyp",
            "private_new": "Privat",
            "category": "Kategorie",
            "solution": "Lösung",
            "difficulty": "Schwierigkeit",
            "explicit": "explizit",
            "quiz_question": "Quizfrage",
            "option1": "Option 1",
            "option2": "Option 2",
            "option3": "Option 3",
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }

class ImageDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Minimale Schwierigkeit")
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY, label="Maximale Schwierigkeit")
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Ältestes Erstelldatum", required=False)
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
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Ältestes Erstelldatum", required=False)
    amount = forms.IntegerField(label="Anzahl")

    def __init__(self, *args, **kwargs):
        super(ImageDownloadForm, self).__init__(*args, **kwargs)
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
    min_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Neuestes Erstelldatum", required=False)
    max_upload_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label="Ältestes Erstelldatum", required=False)
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