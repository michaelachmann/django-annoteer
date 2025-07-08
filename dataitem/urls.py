from django.urls import path
from .views import (
    dataitem_list,
    dataitem_detail,
    # dataitem_create,
    dataitem_update,
    dataitem_delete,
    dataitem_import
)

app_name = "dataitems"

urlpatterns = [
    path("", dataitem_list, name="dataitem_list"),
    path("<int:pk>/", dataitem_detail, name="dataitem_detail"),
    #path("create/", dataitem_create, name="dataitem_create"),
    path("<int:pk>/update/", dataitem_update, name="dataitem_update"),
    path("<int:pk>/delete/", dataitem_delete, name="dataitem_delete"),
    path("<int:pk>/import/", dataitem_import, name="dataitem_import")

]
