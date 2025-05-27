from django import forms
from .models import Annotation


class AnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ["label", "description"]
