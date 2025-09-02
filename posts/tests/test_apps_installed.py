# posts/tests/test_apps_installed.py
from django.test import TestCase
from django.conf import settings
from django.apps import apps

class AppsInstalledTest(TestCase):
    """Test that the posts app is properly installed and configured."""
    
    def test_posts_app_is_in_installed_apps(self):
        """
        Ensure 'posts' is listed in INSTALLED_APPS.
        This is a minimal health check for app registration.
        """
        self.assertIn(
            "posts", 
            settings.INSTALLED_APPS,
            "Expected 'posts' to be in INSTALLED_APPS but it was missing."
        )

    def test_posts_app_config_name_is_correct(self):
        """
        Ensure the AppConfig for 'posts' is discoverable and has the right name.
        """
        config = apps.get_app_config("posts")
        self.assertEqual(
            config.name, 
            "posts", 
            "AppConfig.name should be 'posts'."
        )