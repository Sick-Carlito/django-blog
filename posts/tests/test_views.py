# posts/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from posts.models import Post

class PostPermissionsTests(TestCase):
    def setUp(self):
        """
        Create three users:
        - normal_user: logged-in but not staff
        - staff_user: logged-in and staff (can create posts)
        - author: staff user who will own a post
        """
        self.normal_user = User.objects.create_user(username="normal", password="pass123")
        self.staff_user = User.objects.create_user(username="staff", password="pass123", is_staff=True)
        self.author = User.objects.create_user(username="author", password="pass123", is_staff=True)

        # Create a post by 'author'
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="Some content",
            author=self.author,
        )

    def test_anonymous_cannot_create_post(self):
        """Anonymous users should be redirected to login when accessing create view."""
        response = self.client.get(reverse("posts:post-create"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login")))

    def test_non_staff_cannot_create_post(self):
        """Non-staff logged-in users get 403 when trying to create a post."""
        self.client.login(username="normal", password="pass123")
        response = self.client.get(reverse("posts:post-create"))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_post(self):
        """Staff users can access the post create page."""
        self.client.login(username="staff", password="pass123")
        response = self.client.get(reverse("posts:post-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")  # form is present

    def test_non_author_cannot_edit_post(self):
        """A staff user who is not the author should get 403 when editing."""
        self.client.login(username="staff", password="pass123")
        response = self.client.get(reverse("posts:post-update", args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_author_can_edit_post(self):
        """The author of the post should be able to edit it."""
        self.client.login(username="author", password="pass123")
        response = self.client.get(reverse("posts:post-update", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")  # edit form visible

    def test_non_author_cannot_delete_post(self):
        """A different staff user cannot delete the post."""
        self.client.login(username="staff", password="pass123")
        response = self.client.get(reverse("posts:post-delete", args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_author_can_delete_post(self):
        """The author should be able to delete their own post."""
        self.client.login(username="author", password="pass123")
        response = self.client.get(reverse("posts:post-delete", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure")
