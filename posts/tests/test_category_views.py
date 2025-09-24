# posts/tests/test_category_views.py
# Tests for Category list/detail views and slug auto-generation.

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post, Category


class CategoryViewTests(TestCase):
    def setUp(self):
        """
        Create user, categories, and posts for testing category views.
        """
        User = get_user_model()
        self.user = User.objects.create_user(
            username="catviewer", password="testpass"
        )

        # Categories
        self.cat1 = Category.objects.create(name="Django", slug="django")
        self.cat2 = Category.objects.create(name="Python", slug="python")

        # Posts linked to categories
        self.post1 = Post.objects.create(
            title="Django Intro",
            slug="django-intro",
            content="Learn Django",
            author=self.user,
        )
        self.post1.categories.add(self.cat1)

        self.post2 = Post.objects.create(
            title="Python Basics",
            slug="python-basics",
            content="Learn Python",
            author=self.user,
        )
        self.post2.categories.add(self.cat2)

    def test_category_list_view_displays_categories(self):
        """
        GET /categories/ should list available categories.
        """
        url = reverse("posts:category-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Django")
        self.assertContains(resp, "Python")

    def test_category_detail_view_lists_posts_in_category(self):
        """
        GET /category/<slug>/ should list posts belonging to that category.
        """
        url = reverse("posts:category-detail", kwargs={"slug": "django"})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # should contain the Django post
        self.assertContains(resp, "Django Intro")
        # should not contain Python post
        self.assertNotContains(resp, "Python Basics")

    def test_category_slug_auto_generated_if_missing(self):
        """
        Creating a Category without a slug should auto-generate it from name.
        """
        c = Category.objects.create(name="Machine Learning")
        self.assertEqual(c.slug, "machine-learning")
