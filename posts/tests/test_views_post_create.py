from django.urls import reverse
from django.test import TestCase, Client
from django.apps import apps
from django.contrib.auth import get_user_model

def get_post_model():
    return apps.get_model("posts", "Post")

def make_user(username="creator@example.com"):
    User = get_user_model()
    return User.objects.create_user(username=username, email=username, password="pass12345")


class PostCreateViewTests(TestCase):
    def setUp(self):
        """
        Set up a client and an authenticated user for the test suite.
        """
        self.client = Client()
        self.user = make_user()
        self.create_url = reverse("posts:post-create")

    def test_anonymous_user_redirected_to_login(self):
        """
        An anonymous user should be redirected to the login page when accessing the create view.
        """
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_authenticated_user_can_access_form(self):
        """
        An authenticated user should be able to access the post creation form successfully.
        """
        self.client.login(username=self.user.username, password="pass12345")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTemplateUsed(response, "posts/post_form.html")

    def test_authenticated_user_can_submit_post_form(self):
        """
        An authenticated user should be able to submit a valid form and create a new Post object.
        """
        self.client.login(username=self.user.username, password="pass12345")
        form_data = {
            "title": "Created via Form",
            "slug": "created-via-form",
            "content": "This is created via the PostCreateView form."
        }
        initial_post_count = get_post_model().objects.count()
        response = self.client.post(self.create_url, form_data, follow=True)
        final_post_count = get_post_model().objects.count()

        self.assertEqual(final_post_count, initial_post_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_post_model().objects.filter(slug="created-via-form").exists())