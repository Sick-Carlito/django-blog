# accounts/tests/test_accounts_registration.py
# TDD tests for accounts app: verify default user model and registration flow.
# Uses django.test.TestCase for DB-backed tests.

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class AccountsRegistrationTests(TestCase):
    """
    Tests:
     - settings.AUTH_USER_MODEL should be the default 'auth.User'
     - GET /accounts/register/ returns 200 and uses the registration template
     - POST to /accounts/register/ creates a user and logs them in
    """

    def setUp(self):
        # test client simulates browser requests
        self.client = Client()

    def test_default_user_model_is_auth_user(self):
        """
        Ensure AUTH_USER_MODEL equals 'auth.User' indicating the default Django user model is used.
        """
        self.assertEqual(settings.AUTH_USER_MODEL, "auth.User")

    def test_register_get_returns_200(self):
        """
        GET the registration page and verify HTTP 200 and template usage.
        """
        url = reverse("accounts:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Template name should be registration/register.html
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_post_creates_user_and_logs_in(self):
        """
        POST a valid registration form and verify:
         - user exists in DB
         - client session contains auth key (logged in)
        """
        url = reverse("accounts:register")
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "safe_password_123",
            "password2": "safe_password_123",
        }
        # POST and follow redirect so the client ends up on the final page
        response = self.client.post(url, data=form_data, follow=True)

        # Debug output
        if response.context and 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")

        # HTTP 200 after following redirect(s)
        self.assertEqual(response.status_code, 200)

        # The user should exist in the DB
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="newuser").exists())

        # The client session should now have an authenticated user id (logged in)
        self.assertIn("_auth_user_id", self.client.session)
    
    def test_register_redirects_to_post_list(self):
        """
        Test that registering a new user redirects to the post list page.
        """
        response = self.client.post(
            reverse("accounts:register"),   # <-- use namespace now
            {
                "username": "testuser",
                "email": "testuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,  # follow redirects
        )

        # Check that user was created
        self.assertTrue(User.objects.filter(username="testuser").exists())

        # Confirm redirect chain contains posts:post-list
        self.assertRedirects(response, reverse("posts:post-list"))

        # Confirm user is logged in
        self.assertTrue(response.context["user"].is_authenticated)
