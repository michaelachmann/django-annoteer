from django import forms
from .models import Dataitem


class DataitemForm(forms.ModelForm):
    class Meta:
        model = Dataitem
        fields = ["name", "description"]

