from django import forms
from .models import Project, Label


# projects/forms.py
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter project name"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter a short description (optional)"
            }),
        }


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["label", "value"]
        widgets = {
            "label": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Positive"
            }),
            "value": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "POS"
            }),
        }
