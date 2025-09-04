# posts/tests/test_views_post_seo.py
# TDD tests for SEO features in PostDetailView.

from django.test import TestCase, Client         # Test framework and client for HTTP simulation
from django.urls import reverse                  # Build URLs by name
from django.apps import apps                     # To fetch models dynamically
from django.contrib.auth import get_user_model  # To create an author user


class PostSEOTest(TestCase):
    """Test suite for SEO features in PostDetailView."""

    def get_post_model(self):
        """
        Helper to find the Post model in the app registry.
        This avoids importing models at module import time (safer for TDD).
        """
        return apps.get_model("posts", "Post")

    def make_author(self, username="seoauthor@example.com"):
        """
        Creates and returns a simple user to use as post author in tests.
        """
        User = get_user_model()
        return User.objects.create_user(
            username=username, 
            email=username, 
            password="pass12345"
        )

    def test_post_detail_contains_canonical_and_meta(self):
        """
        Post detail view should include SEO elements:
          - Canonical link tag
          - Meta description tag  
          - Open Graph title and description tags
        """
        Post = self.get_post_model()
        author = self.make_author()
        
        # Create a post with content suitable for SEO testing
        post = Post.objects.create(
            title="SEO Post",
            slug="seo-post", 
            content="This is some SEO test content for checking meta description generation.",
            author=author,
        )
        
        client = Client()
        url = reverse("posts:post-detail", kwargs={"slug": post.slug})
        response = client.get(url)
        
        self.assertEqual(response.status_code, 200, "Expected 200 OK for post detail.")
        
        body = response.content.decode()
        
        # Canonical tag - should point to the current post URL
        expected_canonical = f'<link rel="canonical" href="http://testserver{url}">'
        self.assertIn(
            expected_canonical, 
            body, 
            f"Expected canonical link {expected_canonical}"
        )
        
        # Meta description tag - should be present for SEO
        self.assertIn(
            '<meta name="description"', 
            body, 
            "Expected meta description tag."
        )
        
        # Open Graph title - should be present for social sharing
        self.assertIn(
            '<meta property="og:title"', 
            body, 
            "Expected og:title meta tag."
        )
        
        # Open Graph description - should be present for social sharing
        self.assertIn(
            '<meta property="og:description"', 
            body, 
            "Expected og:description meta tag."
        )