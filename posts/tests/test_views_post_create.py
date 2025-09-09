# posts/tests/test_views_post_create.py
# TDD for admin-only post creation.
#
# We verify three behaviors:
# 1) Anonymous users are redirected to LOGIN_URL when requesting the create page.
# 2) Authenticated non-staff users receive 403 Forbidden.
# 3) Staff users can access the form and create a Post successfully.

from django.test import TestCase, Client         # Test framework and client for HTTP simulation
from django.urls import reverse                  # reverse() builds URLs by name
from django.apps import apps                     # apps.get_model to fetch Post without direct import
from django.contrib.auth import get_user_model  # To create users
from django.conf import settings                 # To read LOGIN_URL for redirect assertions


class PostCreateViewTest(TestCase):
    """Test suite for admin-only post creation with authentication and permission checks."""

    def get_post_model(self):
        """
        Fetch the Post model from the app registry.
        Using the registry avoids import ordering issues in TDD.
        """
        return apps.get_model("posts", "Post")

    def make_user(self, username="user@example.com", is_staff=False):
        """
        Create a user with optional staff flag.
        - username doubles as the email for simplicity.
        - is_staff=True denotes an admin/staff user (allowed to create posts).
        """
        User = get_user_model()                     # Get the active User model
        user = User.objects.create_user(
            username=username,                      # Set username
            email=username,                         # Set email (same as username here)
            password="pass12345",                   # Set a known password for login()
        )
        if is_staff:                                # If admin privilege requested
            user.is_staff = True                    # Mark as staff (admin UI access)
            user.save()                             # Persist the change
        return user                                 # Return the created user

    def test_create_view_redirects_anonymous_to_login(self):
        """
        Anonymous users should be redirected to the login page when accessing /create/.
        """
        client = Client()                           # New test client (not logged in)
        url = reverse("posts:post-create")          # Build /create/ URL from its name
        response = client.get(url)                  # GET the create page
        
        self.assertEqual(
            response.status_code, 
            302, 
            "Expected redirect for anonymous users."
        )
        
        # Django redirects to settings.LOGIN_URL (default: '/accounts/login/') with ?next=<requested_path>
        self.assertTrue(
            response.url.startswith(settings.LOGIN_URL),
            f"Expected redirect to LOGIN_URL; got {response.url}"
        )

    def test_create_view_returns_403_for_non_staff(self):
        """
        Logged-in non-staff users should receive 403 Forbidden when accessing /create/.
        """
        client = Client()                           # Test client
        user = self.make_user(username="nonstaff@example.com", is_staff=False)  # Regular user (not staff)
        
        # Log in the non-staff user
        login_successful = client.login(username=user.username, password="pass12345")
        self.assertTrue(login_successful, "User should be able to log in.")

        url = reverse("posts:post-create")          # Build create URL
        response = client.get(url)                  # Attempt to open the form
        
        self.assertEqual(
            response.status_code, 
            403, 
            "Expected 403 Forbidden for non-staff users."
        )

    def test_staff_user_can_access_form_and_create_post(self):
        """
        Staff users should access the form (200 OK) and submit a valid POST to create a Post.
        """
        client = Client()                           # Test client
        admin = self.make_user(username="staff@example.com", is_staff=True)  # Staff/admin user
        
        # Log in as staff
        login_successful = client.login(username=admin.username, password="pass12345")
        self.assertTrue(login_successful, "Staff user should be able to log in.")

        # Access the form (GET)
        url = reverse("posts:post-create")          # /create/
        response = client.get(url)                  # Open the create page
        
        self.assertEqual(
            response.status_code, 
            200, 
            "Staff should see the creation form."
        )
        
        # Ensure the expected template is used
        template_names = [t.name for t in response.templates if t.name]  # List templates used
        self.assertIn(
            "posts/post_form.html", 
            template_names, 
            "Expected posts/post_form.html template."
        )
        self.assertIn("form", response.context, "CreateView should provide a 'form' in context.")

        # Submit the form (POST)
        form_data = {
            "title": "Admin Post",
            "slug": "admin-post",
            "content": "Created by staff user.",
        }
        response = client.post(url, form_data, follow=True)  # Submit and follow redirect

        Post = self.get_post_model()                # Fetch Post model
        
        # Verify the object exists and was authored by the staff user
        self.assertTrue(
            Post.objects.filter(slug="admin-post", author=admin).exists(),
            "Expected the post to be created with staff user as author."
        )
        self.assertEqual(
            response.status_code, 
            200, 
            "Expected 200 OK after follow."
        )
        
        # Additional verification - check post details
        created_post = Post.objects.get(slug="admin-post")
        self.assertEqual(created_post.title, "Admin Post", "Post title should match form data.")
        self.assertEqual(created_post.content, "Created by staff user.", "Post content should match form data.")
        self.assertEqual(created_post.author, admin, "Post author should be the staff user.")