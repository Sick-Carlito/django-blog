# posts/tests/test_category_model.py
# Tests for Category model and linking it to Post (TDD).
#
# These use django.test.TestCase so they create a test database.
# Place this file under posts/tests/

from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Category  # Expect Category to exist (RED initially)


class CategoryModelTests(TestCase):
    """
    Tests for Category creation and the Post <-> Category relationship.
    """

    def setUp(self):
        """
        Create a sample user and post for linking tests.
        """
        User = get_user_model()                          # support custom user models
        self.user = User.objects.create_user(
            username="catuser", password="testpass"
        )

        # Create a sample post we'll attach categories to
        self.post = Post.objects.create(
            title="Category Test Post",
            slug="category-test-post",
            content="Testing categories",
            author=self.user,
        )

    def test_category_can_be_created(self):
        """
        You should be able to create a Category with name and slug.
        """
        c = Category.objects.create(name="Tech", slug="tech")
        self.assertTrue(Category.objects.filter(slug="tech").exists())

    def test_post_has_categories_m2m_field(self):
        """
        Post model must have a many-to-many field 'categories'.
        """
        field = Post._meta.get_field("categories")
        # verify it's a many-to-many field
        self.assertTrue(field.many_to_many)

    def test_link_category_to_post_and_reverse_lookup(self):
        """
        You should be able to add a Category to a Post and query reverse.
        """
        c = Category.objects.create(name="Django", slug="django")
        # attach category to the post
        self.post.categories.add(c)
        # The post should appear in the category's posts queryset
        self.assertIn(self.post, c.posts.all())
        # The category should appear in the post's categories queryset
        self.assertIn(c, self.post.categories.all())
