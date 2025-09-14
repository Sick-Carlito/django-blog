# accounts/tests/test_profile_update_view.py
# Tests for ProfileUpdateView (TDD-style) using django.test.TestCase.
#
# Tests:
#  - profile update page requires login (redirects anonymous to login)
#  - logged-in user can GET the profile edit form (200)
#  - POST with new bio and avatar updates the Profile and saves the avatar file
#
import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.apps import apps
from django.conf import settings

# Create a temporary MEDIA_ROOT for file tests so we don't pollute real media folder
TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix="test_media_")

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProfileUpdateViewTests(TestCase):
    """
    Tests for profile update page under temporary MEDIA_ROOT.
    The temp directory is removed in tearDownClass.
    """

    @classmethod
    def tearDownClass(cls):
        """
        Remove temporary media root directory after tests finish.
        """
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """
        Create user and ensure Profile exists (signals or get_or_create).
        """
        User = get_user_model()                       # get user model (supports custom models)
        # Create user for tests
        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="testpass123"
        )
        # If signals didn't auto-create Profile, create/get it here to be safe
        Profile = apps.get_model("accounts", "Profile")
        profile, _ = Profile.objects.get_or_create(user=self.user)
        self.profile = profile

    def test_login_required_redirects_to_login(self):
        """
        Anonymous GET to profile edit should redirect to login page.
        """
        url = reverse("accounts:profile-update")      # namespaced URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_get_profile_update_form_and_post_changes(self):
        """
        Logged-in user can GET the profile update page (200) and POST updates:
         - new bio should be saved
         - avatar file should exist under MEDIA_ROOT
        """
        # Login the user (use client.login to simulate auth)
        login_ok = self.client.login(username="profileuser", password="testpass123")
        self.assertTrue(login_ok)

        url = reverse("accounts:profile-update")

        # GET the profile update form
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 200)
        # 'form' should be present in context for rendering
        self.assertIn("form", response_get.context)

        # Build a small valid GIF binary and upload as avatar
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00'
            b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile("avatar.gif", small_gif, content_type="image/gif")

        new_bio = "Updated bio from test"

        # POST the form with avatar file and new bio; use follow=True to follow redirects
        response_post = self.client.post(
            url,
            {"bio": new_bio, "avatar": uploaded},
            follow=True,
        )

        # After successful POST we expect a 200 final response (after redirect)
        self.assertEqual(response_post.status_code, 200)

        # Refresh profile from DB and assert changes
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, new_bio)

        # Avatar file should have been saved under MEDIA_ROOT
        self.assertTrue(bool(self.profile.avatar.name), "Avatar name should be set")
        self.assertTrue(os.path.exists(self.profile.avatar.path), msg="Avatar file should exist on disk")

        # Clean up saved file
        self.profile.avatar.delete(save=True)