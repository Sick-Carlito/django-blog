# posts/tests/test_views_post_detail.py
# TDD tests for PostDetailView and its URL wiring.

from django.test import TestCase, Client         # Test framework and client for HTTP simulation
from django.urls import reverse, resolve        # reverse -> build URL by name; resolve -> get view for a URL
from django.apps import apps                    # To fetch models dynamically
from django.contrib.auth import get_user_model # To create an author user


class PostDetailViewTest(TestCase):
    """Test suite for PostDetailView and its URL configuration."""

    def get_post_model(self):
        """
        Helper to find the Post model in the app registry.
        This avoids importing models at module import time (safer for TDD).
        """
        return apps.get_model("posts", "Post")

    def make_author(self, username="author@example.com"):
        """
        Creates and returns a simple user to use as post author in tests.
        """
        User = get_user_model()
        return User.objects.create_user(
            username=username, 
            email=username, 
            password="pass12345"
        )

    def test_detail_url_resolves_to_post_detail_view(self):
        """
        Reverse the named URL for post-detail and ensure it resolves to our class-based view.
        """
        # Build a sample URL for slug 'example-slug' (the pattern must be registered for this to resolve)
        url = reverse("posts:post-detail", kwargs={"slug": "example-slug"})
        resolver_match = resolve(url)        # Resolve the URL to a ResolverMatch object
        
        # Ensure the resolved callable's dotted path contains our view class path.
        self.assertIn(
            "posts.views.PostDetailView", 
            resolver_match._func_path, 
            "URL does not resolve to PostDetailView."
        )

    def test_post_detail_view_renders_template_and_shows_content(self):
        """
        Create a Post and ensure the detail view:
          - returns HTTP 200
          - uses 'posts/post_detail.html' template
          - includes the post title and full content in the response body
          - provides the post in context as 'post'
        """
        Post = self.get_post_model()
        author = self.make_author()
        
        # Create a post to fetch by slug
        post = Post.objects.create(
            title="My Detail Post", 
            slug="my-detail-post", 
            content="Hello detail content", 
            author=author
        )
        
        client = Client()
        response = client.get(
            reverse("posts:post-detail", kwargs={"slug": post.slug})
        )  # GET the detail URL
        
        # Check HTTP status
        self.assertEqual(
            response.status_code, 
            200, 
            "Expected 200 OK for existing post detail."
        )
        
        # Check template used
        templates_used = [t.name for t in response.templates if t.name]
        self.assertIn(
            "posts/post_detail.html", 
            templates_used, 
            "Expected posts/post_detail.html template."
        )
        
        # Check content presence
        body = response.content.decode()
        self.assertIn(
            "My Detail Post", 
            body, 
            "Expected post title in response body."
        )
        self.assertIn(
            "Hello detail content", 
            body, 
            "Expected post content in response body."
        )
        
        # Context object should include 'post' per our expected context_object_name
        self.assertIn("post", response.context, "Expected 'post' in context.")
        self.assertEqual(
            response.context["post"].slug, 
            post.slug, 
            "Context post should match the requested slug."
        )

    def test_post_detail_returns_404_for_missing_slug(self):
        """
        Requesting a non-existent slug should return 404 Not Found.
        """
        client = Client()
        response = client.get(
            reverse("posts:post-detail", kwargs={"slug": "no-such-slug"})
        )
        
        self.assertEqual(
            response.status_code, 
            404, 
            "Expected 404 for non-existent post slug."
        )