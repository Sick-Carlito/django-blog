# posts/tests/test_admin_integration.py
# TDD tests for admin integration:
# 1) Confirm the Post model is registered with the Django admin site
# 2) Confirm an admin user can add a Post via the admin add page

from django.test import TestCase, Client     # Test framework and client for browser simulation
from django.contrib import admin             # Access admin registry
from django.apps import apps                 # Fetch model from app registry
from django.contrib.auth import get_user_model  # To create a superuser in tests
from django.urls import reverse              # Reverses named URLs like admin add


class AdminIntegrationTest(TestCase):
    """Test suite for Django admin integration with the Post model."""

    def test_post_model_registered_in_admin(self):
        """
        Assert that the posts.Post model is registered in admin.site._registry.
        admin.site._registry maps model classes to their ModelAdmin instances.
        """
        Post = apps.get_model("posts", "Post")  # Lookup Post model by app_label and model name
        self.assertIn(
            Post, 
            admin.site._registry, 
            "Post model is not registered in the admin site."
        )

    def test_admin_user_can_add_post_via_admin(self):
        """
        Create a superuser, log in using the test client, POST to the admin add form,
        and verify the post was created in the DB.
        """
        User = get_user_model()
        
        # Create a superuser account for use during this test
        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123"
        )
        
        client = Client()                       # Instantiate the Django test client
        
        # Login via client using credentials above
        logged_in = client.login(
            username="adminuser",
            password="adminpass123",
        )
        self.assertTrue(logged_in, "Failed to log in the test superuser to the admin client.")
        
        # Prepare form data for the admin add view. For FK 'author' we supply the user's pk.
        form_data = {
            "title": "Admin Created Post",
            "slug": "admin-created-post",
            "content": "Content created via admin in test.",
            "author": str(admin_user.pk),       # Admin form accepts the pk for FK fields
            "_save": "Save",                    # The admin submit button name to persist the model
        }
        
        # Use Django's reversing utility to get the admin add URL for posts.Post
        add_url = reverse("admin:posts_post_add")  # admin:<app_label>_<modelname>_add
        
        # POST to the admin add URL and follow redirects so we can inspect final response
        response = client.post(add_url, form_data, follow=True)
        self.assertEqual(
            response.status_code, 
            200, 
            "POST to admin add returned non-200 status."
        )
        
        # Verify the object exists in the DB now
        Post = apps.get_model("posts", "Post")
        self.assertTrue(
            Post.objects.filter(slug="admin-created-post").exists(),
            "Post not created via admin form."
        )