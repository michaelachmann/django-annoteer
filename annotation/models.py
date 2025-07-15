from django.db import models
from django.contrib.auth.models import User
from dataitem.models import Dataitem
from projects.models import Label, Project


class Annotation(models.Model):
    #project = models.ForeignKey(Project, on_delete=models.CASCADE)
    annotated_by = models.ForeignKey(User, related_name="annotations", on_delete=models.CASCADE)
    dataitem = models.ForeignKey(Dataitem, related_name="annotations" , on_delete=models.CASCADE)

    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='last_modified_by'
    )
    last_modified_at = models.DateTimeField(auto_now_add=True)


class AnnotationLabel(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE,
                                   related_name="annotation_labels")
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
