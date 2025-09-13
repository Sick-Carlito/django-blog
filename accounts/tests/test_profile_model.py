# accounts/tests/test_profile_model.py
# Tests for the Profile model (avatar + bio) using django.test.TestCase.
#
# Tests:
#  - A Profile is created automatically when a User is created.
#  - Avatar upload works and file is saved to MEDIA_ROOT.
#  - __str__ returns a helpful representation.

import shutil
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from django.apps import apps


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="test_media_"))
class ProfileModelTests(TestCase):
    """
    Tests use a temporary MEDIA_ROOT to avoid polluting developer media.
    The temporary directory is removed in tearDownClass.
    """

    @classmethod
    def tearDownClass(cls):
        """
        Remove the temporary MEDIA_ROOT directory after tests finish.
        """
        super().tearDownClass()
        # remove the temporary directory and any files inside it
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """
        Create a user for tests. The Profile should be auto-created by signals.
        """
        User = get_user_model()
        self.user = User.objects.create_user(username="profileuser", password="pass12345", email="p@example.com")
        # Get the Profile model using the app registry (avoids direct import timing issues)
        self.Profile = apps.get_model("accounts", "Profile")

    def test_profile_created_on_user_creation(self):
        """
        After creating a user, a Profile instance should exist and be linked to the user.
        """
        profile = self.Profile.objects.get(user=self.user)  # should exist
        # assert fields exist and default values are correct
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, "")  # default blank bio

    def test_avatar_upload_saves_file(self):
        """
        Upload a tiny GIF image via SimpleUploadedFile to the avatar field and
        verify the file is saved under MEDIA_ROOT/avatars/.
        """
        profile = self.Profile.objects.get(user=self.user)

        # minimal valid GIF bytes (1x1 gif)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00'
            b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile("avatar.gif", small_gif, content_type="image/gif")

        # assign and save
        profile.avatar.save("avatar.gif", uploaded, save=True)

        # file path should exist and start with MEDIA_ROOT
        self.assertTrue(profile.avatar.path.startswith(settings.MEDIA_ROOT))
        # ensure file exists on disk
        import os
        self.assertTrue(os.path.exists(profile.avatar.path))

        # cleanup file
        profile.avatar.delete(save=True)

    def test_profile_str(self):
        """
        __str__ should return a readable string including username.
        """
        profile = self.Profile.objects.get(user=self.user)
        self.assertIn(self.user.username, str(profile))