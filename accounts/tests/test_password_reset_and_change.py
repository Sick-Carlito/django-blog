# These tests simulate the user steps:
# - request password reset (POST email) -> ensure email sent and redirect to done page
# - follow the reset link from the email, set a new password -> ensure redirect to complete
# - login with the new password -> success
# - password change (authenticated user): change password -> redirect to done -> login with new password
#
# Run with: python manage.py test accounts.tests.test_password_reset_and_change

import re
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail


class PasswordResetAndChangeTests(TestCase):
    """
    Tests the password reset and password change flows.
    """

    def setUp(self):
        """
        Create a user with email so we can request a password reset.
        """
        User = get_user_model()
        self.user_password = "OrigPass123!"
        self.user = User.objects.create_user(
            username="pwuser",
            email="pwuser@example.com",
            password=self.user_password,
        )

    def test_password_reset_flow(self):
        """
        1) POST to password_reset with an existing email -> redirect to password_reset_done
        2) Verify an email was sent and contains a reset link
        3) GET the reset link and POST new password -> redirect to password_reset_complete
        4) Log in with the new password successfully
        """
        # 1) Request password reset
        reset_url = reverse("accounts:password_reset")
        response = self.client.post(reset_url, {"email": self.user.email})

        # View should redirect to the done page
        self.assertRedirects(response, reverse("accounts:password_reset_done"))

        # 2) An email should have been sent
        self.assertEqual(len(mail.outbox), 1, "Expected one email in outbox.")
        email = mail.outbox[0]

        # The email body should contain a URL to the password reset confirm view.
        # Extract the absolute URL from the email body (http://testserver/...)
        match = re.search(r"http://testserver(.+)", email.body)
        self.assertIsNotNone(match, "No URL found in password reset email body.")
        reset_path = match.group(1)  # path portion like /accounts/reset/<uidb64>/<token>/

        # 3) Visit the password reset confirm page (GET) to display form
        get_resp = self.client.get(reset_path)
        self.assertEqual(get_resp.status_code, 200, "Expected 200 when GET reset confirm page.")

        # POST new password to the same reset confirm URL
        new_password = "NewStrongPass123!"
        post_resp = self.client.post(
            reset_path,
            {"new_password1": new_password, "new_password2": new_password},
        )

        # After successful POST, view should redirect to the complete page
        self.assertRedirects(post_resp, reverse("accounts:password_reset_complete"))

        # 4) Now login with the new password
        login_ok = self.client.login(username=self.user.username, password=new_password)
        self.assertTrue(login_ok, "Should be able to login with the new password after reset.")

    def test_password_change_flow(self):
        """
        Authenticated user can change password using password_change view.
        Steps:
        - login, visit change form (GET)
        - POST old_password + new_password1/2 -> redirect to password_change_done
        - logout and login with new password succeeds
        """
        # login first using initial password
        login_ok = self.client.login(username=self.user.username, password=self.user_password)
        self.assertTrue(login_ok, "Login should succeed with original password.")

        # GET password change form
        change_url = reverse("accounts:password_change")
        get_resp = self.client.get(change_url)
        self.assertEqual(get_resp.status_code, 200, "Password change form should be accessible to logged-in user.")

        # POST password change
        new_password = "ChangedPass123!"
        post_resp = self.client.post(
            change_url,
            {
                "old_password": self.user_password,
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )

        # Should redirect to password_change_done
        self.assertRedirects(post_resp, reverse("accounts:password_change_done"))

        # Logout then login with the new password to verify change applied
        self.client.logout()
        login_ok_after = self.client.login(username=self.user.username, password=new_password)
        self.assertTrue(login_ok_after, "Login should succeed with changed password.")