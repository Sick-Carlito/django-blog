# accounts/views.py
"""
Registration view using the custom RegistrationForm.
"""


from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from .models import Profile
from .forms import ProfileForm


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



class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile_form.html"
    success_url = reverse_lazy("accounts:profile-update")

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile