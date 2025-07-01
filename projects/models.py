from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    LABEL_TYPES = {
        'SI': 'Single-Label (Radio)',
        'MU': 'Multi-Label (Checkbox)'
    }

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    instructions = models.TextField(blank=True)

    label_type = models.CharField(
        max_length=2,
        choices=LABEL_TYPES
    )

    num_annotators = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Label(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ('project', 'label')