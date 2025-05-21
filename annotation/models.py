from django.db import models
from django.contrib.auth.models import User
from django import forms

class Annotation(models.Model):
    STATUS_CHOICES = [
        (1, 'Unannotated'),
        (2, 'Annotated'),
        (3, 'Finished Annotation')
    ]
    text = models.TextField(blank=False) #choose text to annotate instead ... open.with etc
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    finished_annotations = forms.ChoiceField(choices=("Ja", "Nein"))
    annotated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    save_finished_annotation = models.BooleanField(default=False)
    last_modified_by= models.ForeignKey(User, on_delete=models.CASCADE, related_name='last_modifiede_by')
    last_modified_at = models.DateTimeField(auto_now_add=True)










# Create your models here.
