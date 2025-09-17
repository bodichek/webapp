from django.urls import path
from . import views

urlpatterns = [
    path("export/", views.export_csv, name="export_csv"),
]
