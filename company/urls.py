from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.company_create, name="company_create"),
    path("detail/", views.company_detail, name="company_detail"),
    path("detail/<int:pk>/", views.company_detail_by_id, name="company_detail_by_id"),
    path("list/", views.CompanyListView.as_view(), name="company_list"),
    path("fetch/", views.fetch_company_data, name="fetch_company_data"),
]