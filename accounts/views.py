# accounts/views.py
# Simple registration view that uses Django's built-in UserCreationForm.

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse


def register_view(request):
    """
    Handle user registration:
    - GET: render registration form
    - POST: validate form, create user, log them in, redirect to the home page
    """
    if request.method == "POST":
        # Bind posted data to the standard UserCreationForm
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user to the database
            user = form.save()
            # Authenticate the newly created user (returns user)
            # Note: authenticate isn't strictly necessary after form.save() on default backend,
            # but it is a good explicit step. We use username and password from the form.cleaned_data.
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=raw_password)
            if user:
                # Log the user in (creates session)
                login(request, user)
                # Redirect to the post list (home). Adjust as needed.
                return redirect(reverse("posts:post-list"))
            # If authentication failed for some reason, redirect to login:
            return redirect(reverse("login"))
    else:
        # If GET request, instantiate an empty form
        form = UserCreationForm()

    # Render the registration template with the form context
    return render(request, "registration/register.html", {"form": form})
