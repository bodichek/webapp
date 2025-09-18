from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_files, name="upload_files"),
    path("list/", views.file_list, name="file_list"),
    path("delete/<int:pk>/", views.file_delete, name="file_delete"),
    path("data/", views.show_data, name="show_data"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
