from django.urls import path
from .views import (
    dataitem_list,
    dataitem_detail,
    dataitem_create,
    dataitem_update,
    dataitem_delete,
    data_import_view,
    batch_detail,
)

app_name = "dataitems"

urlpatterns = [
    path("<int:project_pk>/", dataitem_list, name="dataitem_list"),
    path("<int:pk>/", dataitem_detail, name="dataitem_detail"),
    path("create/", dataitem_create, name="dataitem_create"),
    path("<int:pk>/update/", dataitem_update, name="dataitem_update"),
    path("<int:pk>/delete/", dataitem_delete, name="dataitem_delete"),
    path("<int:project_pk>/import/", data_import_view, name="data_import"),
    path("batch/<int:pk>/", batch_detail, name="batch_detail"),

]
