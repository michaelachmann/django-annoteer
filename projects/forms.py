from django import forms
from .models import Project
from django import forms
from .models import Project
from .models import Label

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

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["label", "value", "id"]
        widgets = {
            "label": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "z. B. Positiv"
            }),
            "value": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "z. B. POS"
            }),
            "id": forms.HiddenInput(),
        }