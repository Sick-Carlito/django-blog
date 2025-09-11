# accounts/urls.py
"""
URL routes for accounts app: register, login, logout.
We use Django's built-in auth views for login/logout and a custom register view.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    # Use builtin LoginView and LogoutView but keep templates in registration/
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/"),
        name="logout",
    ),
]
