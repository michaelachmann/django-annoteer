from django import forms
from .models import Project, Label


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
class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["label", "value"]
        widgets = {
            "label": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Visible label (e.g. Positive)"
            }),
            "value": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Machine-readable key (e.g. POS)"
            }),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def clean_value(self):
        value = self.cleaned_data["value"]
        if self.project:
            qs = Label.objects.filter(project=self.project, value__iexact=value)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This value already exists in this project.")
        return value