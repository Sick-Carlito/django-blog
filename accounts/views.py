# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

def register_view(request):
    """
    Handle user registration:
    - GET: render registration form
    - POST: validate form, create user, log them in, redirect to the home page
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user to the database
            user = form.save()
            # Log them in directly (no need to call authenticate again)
            login(request, user)
            # Redirect to PostListView
            return redirect(reverse("posts:post-list"))
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})
