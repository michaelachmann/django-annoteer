from django.urls import path
from .views import (
    project_list,
    project_detail,
    project_create,
    project_update,
    project_delete, label_manage,
)

app_name = "projects"

urlpatterns = [
    path("", project_list, name="project_list"),
    path("<int:pk>/", project_detail, name="project_detail"),
    path("create/", project_create, name="project_create"),
    path("<int:pk>/update/", project_update, name="project_update"),
    path("<int:pk>/delete/", project_delete, name="project_delete"),

    path("<int:pk>/label/", label_manage, name="label_manage"),

    path("<int:pk>/label/", label_manage, name="label_manage")

]
