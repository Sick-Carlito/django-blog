from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import get_user_model
from django.conf import settings


class PostDeleteViewTests(TestCase):
    """
    TestCase that verifies delete view permissions & behavior:
    - anonymous -> redirect to login
    - non-author authenticated -> 403
    - staff (not author) -> 403 (we enforce author-only)
    - author -> can GET confirmation and POST deletion, object removed
    """

    def setUp(self):
        """
        Create three users and one post:
        - author: the owner of the post (allowed to delete)
        - other: a logged-in non-author user (forbidden)
        - staff: is_staff=True but NOT the author (still forbidden)
        """
        User = get_user_model()

        # Create author user (post author)
        self.author = User.objects.create_user(
            username="author_user",
            email="author@example.com",
            password="pass12345",
        )

        # Create non-author user
        self.other = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="pass12345",
        )

        # Create staff user who is not the author
        self.staff = User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="pass12345",
        )
        self.staff.is_staff = True
        self.staff.save()

        # Create a Post instance authored by 'author'
        Post = apps.get_model("posts", "Post")
        self.post = Post.objects.create(
            title="Delete Me",
            slug="delete-me",
            content="Please delete me",
            author=self.author,
        )

        # Test client for HTTP requests
        self.client = Client()

    def delete_url(self):
        """Helper: return the delete URL for the test post using its slug."""
        return reverse("posts:post-delete", kwargs={"slug": self.post.slug})

    def test_anonymous_redirects_to_login(self):
        """Anonymous user GET should redirect to LOGIN_URL with ?next=..."""
        url = self.delete_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_non_author_gets_403(self):
        """Logged-in non-author should receive HTTP 403 on GET."""
        self.client.login(username="other_user", password="pass12345")
        url = self.delete_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_staff_but_not_author_gets_403(self):
        """Even staff users who are not the author should be forbidden."""
        self.client.login(username="staff_user", password="pass12345")
        url = self.delete_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_author_can_get_confirm_and_delete_post(self):
        """
        Author can GET the confirmation page (200 + template),
        and POST to delete the post (object removed).
        """
        # Log in as author
        self.client.login(username="author_user", password="pass12345")

        url = self.delete_url()

        # GET the confirmation page
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, "posts/post_confirm_delete.html")
        self.assertIn("post", response_get.context)

        # Submit POST to actually delete the object; follow redirects
        response_post = self.client.post(url, follow=True)
        self.assertEqual(response_post.status_code, 200)

        Post = apps.get_model("posts", "Post")
        # The post should be deleted from the DB
        self.assertFalse(Post.objects.filter(slug="delete-me").exists())