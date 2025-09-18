from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from filesapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("parsing/", include("parsing.urls")),
    path("csvapp/", include("csvapp.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("company/", include("company.urls")),
    path("files/", include("filesapp.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    path("", TemplateView.as_view(template_name="welcome.html"), name="welcome"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("list/", views.file_list, name="file_list"),

]

# 🔹 Obsluha media souborů (PDF, obrázky, atd.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
