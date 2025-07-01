from django.contrib import admin
from .models import Project, Label

# Register your models here.
admin.site.register(Project)
admin.site.register(Label)