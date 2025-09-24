# posts/urls.py
from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, CategoryListView, CategoryDetailView

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="post-list"),
    path("create/", PostCreateView.as_view(), name="post-create"),
    # Move category URLs BEFORE the generic slug pattern
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    # Keep post-specific patterns
    path("<slug:slug>/edit/", PostUpdateView.as_view(), name="post-update"),
    path("<slug:slug>/delete/", PostDeleteView.as_view(), name="post-delete"),
    # Generic slug pattern goes LAST
    path("<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
]