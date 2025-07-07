from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from projects.models import Project

class Meta:
    unique_together = ("project", "external_id")

class Dataitem(models.Model):
    batch = models.ForeignKey(
        "DataBatch",
        on_delete=models.CASCADE,
        related_name="dataitems",
        null=True,
        blank=True
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255)   # ❌ NO unique=True here
    text = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "external_id")

    def __str__(self):
        return self.name


class DataBatch(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="batches")
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.project.name})"
