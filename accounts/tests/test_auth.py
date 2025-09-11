# accounts/tests/test_auth.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthFlowTests(TestCase):
    def setUp(self):
        """
        Create a test user that we can log in with.
        """
        self.user = User.objects.create_user(
            username="loginuser",
            password="LoginPass123!"
        )

    def test_login_redirects_to_post_list(self):
        """
        Login should redirect to the post list page.
        """
        response = self.client.post(
            reverse("login"),   # default Django login view
            {
                "username": "loginuser",
                "password": "LoginPass123!",
            },
            follow=True,
        )

        # Confirm redirect to post list
        self.assertRedirects(response, reverse("posts:post-list"))

        # Confirm user is logged in
        self.assertTrue(response.context["user"].is_authenticated)

    """
    def test_logout_redirects_to_login(self):
        """
        #Logout should redirect to login page.
    """
        # First login
        self.client.login(username="loginuser", password="LoginPass123!")

            # Now logout
        response = self.client.get(reverse("logout"), follow=True)

            # Confirm redirect (default logout redirect is LOGIN_URL or /accounts/login/)
        self.assertRedirects(response, reverse("login"))

            # Confirm user is logged out
        self.assertFalse(response.context["user"].is_authenticated)
    """
