from django import forms
from .models import Project


# projects/forms.py
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "instructions", "label_type", "num_annotators"]
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
            "instructions": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter instructions (optional)"
            }),
            "label_type": forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Select label-type (optional)"
            }),
            "num_annotators": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter number of annotators (optional)"
            })
        }
