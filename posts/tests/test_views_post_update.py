from django.test import TestCase, Client                       # TestCase for DB tests, Client simulates requests
from django.urls import reverse                               # reverse() builds URLs by name
from django.contrib.auth import get_user_model                # get_user_model() to support custom user models
from django.apps import apps                                   # apps.get_model() avoids direct import timing issues
from django.conf import settings                              # settings.LOGIN_URL for redirect assertions

class PostUpdateViewTests(TestCase):
    """
    Tests for PostUpdateView:
      - anonymous users -> redirect to login
      - non-author authenticated users -> 403
      - staff but not author -> 403 (we enforce author-only)
      - author can GET form and POST updates successfully
    """

    def setUp(self):
        """
        Create test users and a Post instance.
        This runs before each test method.
        """
        User = get_user_model()                                # Get the active User model
        # Create author user (will be the post.author)
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="pass12345",
        )
        # Create regular non-author user
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass12345",
        )
        # Create staff user who is NOT the author (should still be forbidden)
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="pass12345",
        )
        self.staff.is_staff = True
        self.staff.save()

        Post = apps.get_model("posts", "Post")                  # Fetch the Post model
        # Create a post authored by self.author
        self.post = Post.objects.create(
            title="Original Title",
            slug="original-title",
            content="Original content",
            author=self.author,
        )

        # Create a client for requests
        self.client = Client()

    def get_update_url(self):
        """
        Helper to build the URL for updating our test post by slug.
        """
        return reverse("posts:post-update", kwargs={"slug": self.post.slug})

    def test_anonymous_user_redirects_to_login(self):
        """
        Anonymous user GET -> should redirect to LOGIN_URL with ?next=...
        """
        url = self.get_update_url()
        response = self.client.get(url)                         # anonymous GET
        self.assertEqual(response.status_code, 302)             # redirect expected
        # Redirect should go to LOGIN_URL (prefix); exact path may include next=...
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_non_author_gets_403(self):
        """
        Logged-in but non-author user should receive HTTP 403 (forbidden).
        """
        self.client.login(username="other", password="pass12345")
        url = self.get_update_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_staff_but_not_author_gets_403(self):
        """
        Even staff users (is_staff=True) who are not the author should be forbidden
        because update is restricted to the post author only.
        """
        self.client.login(username="staff", password="pass12345")
        url = self.get_update_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_author_can_get_form_and_update_post(self):
        """
        The post author should be able to GET the update form and POST updated data.
        The Post object in DB should reflect changes after a successful POST.
        """
        # Log in as the author
        self.client.login(username="author", password="pass12345")

        url = self.get_update_url()

        # GET the form page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Ensure the form template is used (we reuse 'posts/post_form.html')
        self.assertTemplateUsed(response, "posts/post_form.html")
        # 'form' should be present in context
        self.assertIn("form", response.context)

        # Now submit updated data (keep slug same to avoid uniqueness issues)
        new_data = {
            "title": "Updated Title",
            "slug": self.post.slug,        # unchanged slug for simplicity
            "content": "Updated content by author",
        }
        response_post = self.client.post(url, new_data, follow=True)
        # After follow=True, final response should be 200
        self.assertEqual(response_post.status_code, 200)

        # Refresh from DB and assert changes
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")
        self.assertEqual(self.post.content, "Updated content by author")