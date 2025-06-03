from django.urls import path
from .views import (
    annotation_list,
    annotation_detail,
    annotation_create,
    annotation_update,
    annotation_delete,
)

app_name = "annotation"

urlpatterns = [
    path("", annotation_list, name="annotation_list"),
    path("<int:pk>/", annotation_detail, name="annotation_detail"),
    path("create/", annotation_create, name="annotation_create"),
    path("<int:pk>/update/", annotation_update, name="annotation_update"),
    path("<int:pk>/delete/", annotation_delete, name="annotation_delete"),
]