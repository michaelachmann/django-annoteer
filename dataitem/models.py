from django.db import models
from django.contrib.auth.models import User


class Dataitem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
