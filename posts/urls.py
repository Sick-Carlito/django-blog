# posts/urls.py
from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="post-list"),
    path("create/", PostCreateView.as_view(), name="post-create"),          # site root -> list view
    path("<slug:slug>/edit/", PostUpdateView.as_view(), name="post-update"),  # <-- update route
    path("<slug:slug>/delete/", PostDeleteView.as_view(), name="post-delete"),  # <-- delete route
   # path("admin/create/", PostCreateAdminView.as_view(), name="post-create-admin"),  # <-- admin-only route
    # Slug-based detail route: e.g., GET /my-first-post/
    # The slug converter captures hyphens, letters, numbers, and underscores.
    path("<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
    
]
