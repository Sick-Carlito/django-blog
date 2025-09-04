# posts/urls.py
from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="post-list"),
    path("create/", PostCreateView.as_view(), name="post-create"),          # site root -> list view
    # Slug-based detail route: e.g., GET /my-first-post/
    # The slug converter captures hyphens, letters, numbers, and underscores.
    path("<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
]
