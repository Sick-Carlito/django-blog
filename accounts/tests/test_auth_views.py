from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AccountsAuthTests(TestCase):
    """
    TestCase covering:
      - registration page GET and successful registration (and auto-login)
      - registration invalid submission (password mismatch)
      - login view authenticates and redirects to post list
      - logout view logs user out and redirects
    """

    def test_register_get_shows_form(self):
        """GET /accounts/register/ returns 200 and uses registration template."""
        url = reverse("accounts:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_post_creates_user_and_logs_in(self):
        """POST valid data -> create user, log in, and redirect to posts list."""
        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(url, data, follow=True)
        User = get_user_model()

        # user created
        self.assertTrue(User.objects.filter(username="newuser").exists())

        # redirect to posts list (home)
        self.assertRedirects(response, reverse("posts:post-list"))

        # logged in
        self.assertTrue(response.context["user"].is_authenticated)

    def test_register_post_invalid_password_mismatch_shows_error(self):
        """Mismatched passwords should NOT create a user and should show form errors."""
        url = reverse("accounts:register")
        data = {
            "username": "baduser",
            "email": "bad@example.com",
            "password1": "abc123",
            "password2": "different",
        }
        response = self.client.post(url, data)
        User = get_user_model()

        # user should not be created
        self.assertFalse(User.objects.filter(username="baduser").exists())

        # response should re-render the form (status 200) with errors on the form
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)

    def test_login_view_authenticates_and_redirects(self):
        """Existing user can login via accounts:login and will be redirected to posts list."""
        User = get_user_model()
        User.objects.create_user(username="loginuser", password="LoginPass123!")
        url = reverse("accounts:login")
        response = self.client.post(url, {"username": "loginuser", "password": "LoginPass123!"}, follow=True)

        # After login should redirect to posts list
        self.assertRedirects(response, reverse("posts:post-list"))
        self.assertTrue(response.context["user"].is_authenticated)

    def test_logout_logs_out_and_redirects(self):
        """Logout will log out the user and redirect to posts list (or configured logout redirect)."""
        User = get_user_model()
        User.objects.create_user(username="logoutuser", password="LogoutPass123!")
        # login first (client.login uses backend, not the view)
        self.client.login(username="logoutuser", password="LogoutPass123!")
        url = reverse("accounts:logout")
        response = self.client.get(url, follow=True)

        # After logout user is anonymous
        self.assertFalse(response.context["user"].is_authenticated)
        # Logged out redirect (we expect posts list)
        self.assertRedirects(response, reverse("posts:post-list"))