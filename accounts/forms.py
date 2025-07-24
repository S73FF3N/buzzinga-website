from django import forms

class DownloadForm(forms.Form):
    def __init__(self, *args, **kwargs):

        queryset = kwargs.pop('queryset')
        super(DownloadForm, self).__init__(*args, **kwargs)
        self.fields['elements'].queryset = queryset

    elements = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple
    )