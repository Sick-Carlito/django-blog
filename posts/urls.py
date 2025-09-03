# posts/urls.py
# URL routes for the 'posts' app.

from django.urls import path                       # path() helper maps routes to views
from .views import PostListView                    # Import our list view

app_name = "posts"                                 # Namespace for URL names: reverse('posts:post-list')

urlpatterns = [
    # Map the site root ('/') to the posts list view
    path("", PostListView.as_view(), name="post-list"),  # as_view() converts class-based view to a callable view
]
