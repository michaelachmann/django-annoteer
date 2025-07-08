from django.contrib.auth.models import User
from django.db import models

from projects.models import Project


# Create your models here.
class Dataitem(models.Model):
    text = models.TextField(blank=True)
    external_id = models.CharField(max_length=255, unique=True) # Does not work -> If unique, we can not have the same ID across different projects.
    # TODO: Fix unique external_id *per Project*, not across the whole databse!

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.external_id}: {self.text}"
