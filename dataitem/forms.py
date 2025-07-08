from django import forms
from .models import Dataitem


class DataitemForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    class Meta:
        model = Dataitem
        fields = ["name", "description"]


class CSVUploadForm(forms.Form):
    file = forms.FileField()

