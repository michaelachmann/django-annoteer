from django.db import models
from django.contrib.auth.models import User
from django import forms
from dataitem.models import Dataitem


class Annotation(models.Model):
    STATUS_CHOICES = [
        (1, 'Unannotated'),
        (2, 'Annotated'),
        (3, 'Finished Annotation')
    ]
    text = models.TextField(blank=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    finished_annotations = forms.ChoiceField(choices=("Ja", "Nein"))
    annotated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.ForeignKey(Dataitem, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    save_finished_annotation = models.BooleanField(default=False)
    dataitem = models.ForeignKey(Dataitem, on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='last_modified_by')
    last_modified_at = models.DateTimeField(auto_now_add=True)
