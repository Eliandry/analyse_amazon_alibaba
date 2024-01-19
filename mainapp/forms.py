from django import forms
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
class ScraperForm(forms.Form):
    my_base_url = forms.URLField(label='Base URL')