# accounts/admin.py
from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile:
    shows user, created_at, updated_at and avatar preview (optional).
    """
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
