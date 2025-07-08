from django.urls import path
from .views import (
    project_list,
    project_detail,
    project_create,
    project_update,
    project_delete,
    project_instructions,

    label_management,
    label_edit,
    label_delete,


)

app_name = "projects"

urlpatterns = [
    path("", project_list, name="project_list"),
    path("<int:pk>/", project_detail, name="project_detail"),
    path("create/", project_create, name="project_create"),
    path("<int:pk>/update/", project_update, name="project_update"),
    path("<int:pk>/delete/", project_delete, name="project_delete"),
    path("<int:pk>/instructions/", project_instructions, name="project_instructions"),

    path("<int:pk>/labels/", label_management, name="label_management"),

    path("labels/<int:pk>/edit/", label_edit, name="label_edit"),
    path("labels/<int:pk>/delete/", label_delete, name="label_delete"),

]
