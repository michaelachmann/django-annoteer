from django import forms
from .models import Dataitem


class DataitemForm(forms.ModelForm):
    class Meta:
        model = Dataitem
        fields = ["name", "description", "text"]





class DataImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file containing 'id' and 'text' columns."
    )

