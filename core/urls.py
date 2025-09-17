from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views   # 👈 důležité

urlpatterns = [
    path("admin/", admin.site.urls),
    path("parsing/", include("parsing.urls")),
    path("csvapp/", include("csvapp.urls")),
    path("finance/", include("finance.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("company/", include("company.urls")),

    # login/logout
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # homepage
    path("", TemplateView.as_view(template_name="welcome.html"), name="welcome"),
    
    path("files/", include("filesapp.urls")),


   
]
