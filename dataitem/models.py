from django.contrib.auth.models import User
from django.db import models

from projects.models import Project


# Create your models here.
class Dataitem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    text = models.TextField(blank=True)


    external_id = models.CharField(max_length=100, unique=True)


    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.external_id}: {self.text}"



