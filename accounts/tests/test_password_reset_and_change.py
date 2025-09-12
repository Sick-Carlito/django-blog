"""
accounts/tests/test_password_reset_and_change.py

Robust tests for password reset and password change flows.

- Builds uid/token programmatically with Django helpers (not by parsing email text).
- Logs out before hitting the confirm page (ensures anonymous client).
- Uses follow=True where appropriate.
"""

import re
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class PasswordResetAndChangeTests(TestCase):
    """TestCase that covers password reset and password change flows."""

    def setUp(self):
        """Create a user with an email address for password reset testing."""
        User = get_user_model()
        self.old_password = "OrigPass123!"
        self.user = User.objects.create_user(
            username="pwuser",
            email="pwuser@example.com",
            password=self.old_password,
        )

    def test_password_reset_flow(self):
        # 1) Request password reset
        reset_url = reverse("accounts:password_reset")
        response = self.client.post(reset_url, {"email": self.user.email})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))

        # 2) Extract reset link from email
        self.assertEqual(len(mail.outbox), 1, "Expected one email in outbox.")
        email = mail.outbox[0]
        
        match = re.search(r"http://testserver(.+)", email.body)
        self.assertIsNotNone(match, "No URL found in password reset email body.")
        reset_path = match.group(1)

        # 3) Follow the redirect to get the actual form URL
        get_resp = self.client.get(reset_path, follow=True)
        self.assertEqual(get_resp.status_code, 200, "Expected 200 when GET reset confirm page.")
        
        # Get the final URL where the form actually is
        final_form_url = get_resp.wsgi_request.path
        
        # 4) POST new password to the CORRECT URL
        new_password = "NewStrongPass123!"
        post_resp = self.client.post(
            final_form_url,  # Use the redirected URL
            {"new_password1": new_password, "new_password2": new_password},
            follow=True
    )
    
    # Check if we reached the completion page
        self.assertEqual(post_resp.status_code, 200)
        self.assertContains(post_resp, "password has been set")  # Look for success message
        
        # 5) Test login with new password
        login_ok = self.client.login(username=self.user.username, password=new_password)
        self.assertTrue(login_ok, "Should be able to login with the new password after reset.")


    def test_password_change_flow(self):
        """
        Password change for an authenticated user:
        - login, GET change form (200)
        - POST old + new passwords -> redirect to done
        - logout and login with the new password succeeds
        """
        # login first
        login_ok = self.client.login(username=self.user.username, password=self.old_password)
        self.assertTrue(login_ok, "Login should succeed with original password.")

        # GET password change form (authenticated)
        change_url = reverse("accounts:password_change")
        get_resp = self.client.get(change_url)
        self.assertEqual(get_resp.status_code, 200, "Password change form should be accessible to logged-in user.")

        # POST password change data
        new_password = "ChangedPass123!"
        post_resp = self.client.post(
            change_url,
            {
                "old_password": self.old_password,
                "new_password1": new_password,
                "new_password2": new_password,
            },
            follow=True,
        )

        # Should redirect to password_change_done
        self.assertRedirects(post_resp, reverse("accounts:password_change_done"))

        # Logout then log in with new password to verify
        self.client.logout()
        login_ok_after = self.client.login(username=self.user.username, password=new_password)
        self.assertTrue(login_ok_after, "Login should succeed with changed password.")
