from django.db import models
from django.contrib.auth.models import User
from django import forms


class Annotate(models.Model):
    STATUS_CHOICES = [
        (1, "Unannotaed"),
        (2, "Annotated"),
        (3, "Finished Annotating")
    ]
    text = models.TextField(blank=False) #Müsste hier ForeignKey stehen um Text aus Datenbank zu öffnen
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    finished_annotations = forms.ChoiceField(choices=("ja","nein"))
    annotated_at = models.DateTimeField(auto_now_add=True)
    annotated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    save_finished_annotation = models.BooleanField(default=False)
    last_modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "last_modified_by")
    last_modified_at = models.DateTimeField(auto_now=True)



