from django import forms
from .models import Dataitem


class DataitemForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    class Meta:
        model = Dataitem
        fields = ["name", "description"]


class CSVUploadForm(forms.Form):
    file = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        pasted_data = self.data.get('pasted_data', '').strip()

        if not file and not pasted_data:
            raise forms.ValidationError("Please upload a file or paste data.")
        return cleaned_data
