# posts/tests/test_post_permissions.py
# TDD tests to ensure post creation/editing is restricted to logged-in users.

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from posts.models import Post


class PostPermissionsTests(TestCase):
    """
    Tests:
      - anonymous users are redirected to login for create & update pages
      - logged-in users can create posts and become the author
      - author can update their post
    """

    def setUp(self):
        # Create two users: one author and one other user
        User = get_user_model()
        self.user = User.objects.create_user(username="author", password="pass123",  is_staff=True)
        self.other = User.objects.create_user(username="other", password="pass123")

        # URL for creating posts (posts.urls should define name='post-create')
        self.create_url = reverse("posts:post-create")

        # Create a sample post authored by self.user for update tests
        self.post = Post.objects.create(
            title="Initial Title",
            slug="initial-title",
            content="Initial content",
            author=self.user,
        )

    def test_create_requires_login(self):
        """
        Anonymous GET to the create URL should redirect to the login page with next param.
        """
        resp = self.client.get(self.create_url)
        # Django's login redirect uses settings.LOGIN_URL; expected redirect contains ?next=<url>
        expected_login = f"{settings.LOGIN_URL}?next={self.create_url}"
        self.assertRedirects(resp, expected_login)

    def test_create_allows_logged_in_user_and_sets_author(self):
        """
        Logged-in user can POST to create a post and becomes the post.author.
        """
        # Login as self.user
        login_ok = self.client.login(username="author", password="pass123")
        self.assertTrue(login_ok, "Login failed for author user in test setup.")

        # Post data to create a new post (slug must be unique)
        data = {
            "title": "New Post by Author",
            "slug": "new-post-by-author",
            "content": "Some content",
        }
        resp = self.client.post(self.create_url, data, follow=True)
        # After follow, final page should be 200
        self.assertEqual(resp.status_code, 200)

        # Verify the post was created and author is self.user
        self.assertTrue(Post.objects.filter(slug="new-post-by-author").exists())
        post = Post.objects.get(slug="new-post-by-author")
        self.assertEqual(post.author, self.user)

    def test_update_requires_login(self):
        """
        Anonymous GET to the update URL should redirect to login.
        """
        update_url = reverse("posts:post-update", kwargs={"slug": self.post.slug})
        resp = self.client.get(update_url)
        expected_login = f"{settings.LOGIN_URL}?next={update_url}"
        self.assertRedirects(resp, expected_login)

    def test_update_allows_author_to_edit(self):
        update_url = reverse("posts:post-update", kwargs={"slug": self.post.slug})
        
        login_ok = self.client.login(username="author", password="pass123")
        self.assertTrue(login_ok)
        
        # Include ALL required fields in POST data
        resp = self.client.post(update_url, {
            "title": "Updated Title", 
            "slug": self.post.slug,      # Include this
            "content": "Updated"
        }, follow=True)
        
        self.assertEqual(resp.status_code, 200)
        
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")
