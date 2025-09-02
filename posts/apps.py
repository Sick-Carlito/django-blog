# posts/apps.py
# App configuration for the 'posts' application.

from django.apps import AppConfig  # Base class for Django app configs


class PostsConfig(AppConfig):
    """
    AppConfig declares metadata for the 'posts' app.
    'name' must match the Python import path of the app package.
    """
    default_auto_field = "django.db.models.BigAutoField"  # Default PK field type for models
    name = "posts"                                       # Python path of the app (package name)
