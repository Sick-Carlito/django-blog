# accounts/urls.py
# URL routes for the accounts app.

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    # Registration page: GET shows form, POST submits.
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
]
