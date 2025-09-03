# posts/tests/test_views_post_list.py
# TDD tests for PostListView and its URL wiring.

from django.test import TestCase, Client         # Test framework and client for browser simulation
from django.urls import reverse, resolve        # reverse() names -> URL, resolve() URL -> view
from django.contrib.auth import get_user_model  # To create an author for posts
from django.utils import timezone               # For timestamp comparisons
from django.apps import apps                    # To import models safely
from django.template.loader import render_to_string  # For template assertions


class PostListViewTest(TestCase):
    """Test suite for PostListView and its URL configuration."""

    def get_post_model(self):
        """
        Helper: fetch the Post model from the registry.
        We avoid direct import at module scope to keep tests robust in TDD flow.
        """
        return apps.get_model("posts", "Post")

    def make_user(self, username="author@example.com", password="pass12345"):
        """
        Helper: create a basic user to assign as post author.
        """
        User = get_user_model()
        return User.objects.create_user(
            username=username, 
            email=username, 
            password=password
        )

    def test_home_url_resolves_to_post_list_view(self):
        """
        The site's home URL ('/') should be named 'posts:post-list' and resolve to our PostListView.
        """
        url = reverse("posts:post-list")        # Build URL from its name; we will wire this to '/'
        resolver_match = resolve(url)           # Resolve the URL to view function/callable
        
        # The resolver gives us the dotted path; verify the class-based view was used
        self.assertIn(
            "posts.views.PostListView", 
            resolver_match._func_path, 
            "Home URL is not wired to PostListView."
        )

    def test_post_list_view_renders_template_and_lists_posts(self):
        """
        The list view should:
          - return HTTP 200
          - use the 'posts/post_list.html' template
          - include post titles in the response body
          - order posts newest first (by created_at desc per model Meta.ordering)
        """
        Post = self.get_post_model()
        author = self.make_user()
        
        # Create two posts at different times to test ordering (newest should appear first)
        older = Post.objects.create(
            title="Older", 
            slug="older", 
            content="A", 
            author=author
        )
        newer = Post.objects.create(
            title="Newer", 
            slug="newer", 
            content="B", 
            author=author
        )
        
        client = Client()
        response = client.get(reverse("posts:post-list"))  # GET the home page
        
        # 200 OK means the view worked
        self.assertEqual(
            response.status_code, 
            200, 
            "Expected 200 OK from PostListView."
        )
        
        # Django test framework tracks which template(s) were used
        templates_used = [t.name for t in response.templates if t.name]
        self.assertIn(
            "posts/post_list.html", 
            templates_used, 
            "Expected template posts/post_list.html to be used."
        )
        
        # Page content should contain both post titles
        content = response.content.decode()
        self.assertIn("Older", content, "Expected 'Older' post title to appear.")
        self.assertIn("Newer", content, "Expected 'Newer' post title to appear.")
        
        # Newer should come before Older in the HTML (ordering by -created_at)
        newer_index = content.index("Newer")
        older_index = content.index("Older")
        self.assertLess(
            newer_index, 
            older_index, 
            "Expected 'Newer' to appear before 'Older' in the list."
        )
        
        # Context should include the queryset. We also expose 'posts' via context_object_name below.
        self.assertIn("object_list", response.context, "Expected 'object_list' in context.")
        self.assertIn("posts", response.context, "Expected 'posts' key in context.")
        self.assertEqual(
            list(response.context["posts"]), 
            list(response.context["object_list"]), 
            "Expected 'posts' and 'object_list' to match."
        )

    def test_post_list_view_empty_state(self):
        """
        With no posts, the page should still render 200 and show a friendly message.
        """
        client = Client()
        response = client.get(reverse("posts:post-list"))
        
        self.assertEqual(
            response.status_code, 
            200, 
            "Expected 200 OK even with no posts."
        )
        
        content = response.content.decode()
        self.assertIn(
            "No posts yet", 
            content, 
            "Expected an empty-state message 'No posts yet' when there are no posts."
        )