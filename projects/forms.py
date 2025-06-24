from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "instructions",
            "label_type",
            "num_annotators",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter project name"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Short description (Markdown supported)"
            }),
            "instructions": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Detailed instructions (Markdown supported)"
            }),
            "label_type": forms.RadioSelect(),
            "num_annotators": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
        }
