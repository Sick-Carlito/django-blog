# accounts/urls.py
# URL routes for the accounts app.

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Registration page: GET shows form, POST submits.
    path("register/", views.register_view, name="register"),
]
