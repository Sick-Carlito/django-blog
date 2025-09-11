# accounts/views.py
"""
Registration view using the custom RegistrationForm.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse
from .forms import RegistrationForm


def register_view(request):
    """
    GET: render an empty registration form.
    POST: validate, save the user, log them in, and redirect to posts list.
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()           # save user with hashed password
            login(request, user)         # log the newly created user in by creating a session
            return redirect(reverse("posts:post-list"))
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})
