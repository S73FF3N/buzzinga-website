from dal import autocomplete, forward
from django import forms
from .models import Tag, Category, Image, Sound, Question, DIFFICULTY

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        form_tag = False
        fields = ('name_de', 'game_type', 'description_de', 'logo', 'private')

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        form_tag = False
        fields = ('solution', 'image_file', 'difficulty', 'explicit', 'tags', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(1, 'game_type'),))}

class SoundForm(forms.ModelForm):
    class Meta:
        model = Sound
        form_tag = False
        fields = ('solution', 'sound_file', 'difficulty', 'explicit', 'tags', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(2, 'game_type'),))}

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        form_tag = False
        fields = ('solution', 'quiz_question', 'option1', 'option2', 'option3', 'difficulty', 'tags', 'explicit', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'),
                   'category': autocomplete.ModelSelect2(url='gamefiles:category-autocomplete', forward=(forward.Const(3, 'game_type'),))}

class ImageDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY)
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY)
    amount = forms.IntegerField()

    class Meta:
        model = Image
        form_tag = False
        fields = ('tags', 'explicit', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'), }

class SoundDownloadForm(forms.ModelForm):
    min_difficulty = forms.ChoiceField(choices=DIFFICULTY)
    max_difficulty = forms.ChoiceField(choices=DIFFICULTY)
    amount = forms.IntegerField()

    class Meta:
        model = Sound
        form_tag = False
        fields = ('tags', 'explicit', 'category', 'private_new')
        widgets = {'tags': autocomplete.ModelSelect2Multiple(url='gamefiles:tag-autocomplete'), }