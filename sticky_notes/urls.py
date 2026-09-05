from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from notes import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("profile/", views.profile, name="profile"),
    path("notes/", include("notes.urls")),
    path("staff/", include("notes.staff_urls")),
]
