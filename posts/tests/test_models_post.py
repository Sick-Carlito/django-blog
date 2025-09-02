# posts/tests/test_models_post.py
# TDD tests describing the Post model we want to build.

from django.test import TestCase                 # Django's test framework
from django.contrib.auth import get_user_model  # Utility to get the active User model
from django.utils import timezone               # For time-based assertions
from django.db import IntegrityError            # Expected when unique constraints are violated
from django.apps import apps                    # To safely look up models by name


class PostModelTest(TestCase):
    """Test suite for the Post model."""

    def get_post_model(self):
        """
        Helper to fetch the Post model from the apps registry without importing it at module import time.
        This avoids ImportError before the model exists (classic TDD).
        """
        try:
            return apps.get_model("posts", "Post")  # Look up model by app label and model name
        except LookupError:
            # If the model isn't registered yet, make the test clearly fail with a helpful message.
            self.fail("Post model is not registered in the 'posts' app.")

    def create_user(self, email="author@example.com", password="pass12345"):
        """
        Helper to create a user for the 'author' ForeignKey.
        Using get_user_model() keeps it compatible with custom user models.
        """
        User = get_user_model()                  # Get the currently configured user model
        return User.objects.create_user(
            username=email,                      # Use email as username for simplicity
            email=email,
            password=password,
        )

    def test_post_model_exists_and_has_required_fields(self):
        """
        The Post model should exist with fields:
        title (str), slug (unique str), content (text),
        created_at (auto timestamp), updated_at (auto timestamp), author (FK to User).
        """
        Post = self.get_post_model()             # Fetch the model (fails helpfully if missing)

        # Create an author user for the FK field
        author = self.create_user()

        # Create a Post record with all required fields
        post = Post.objects.create(
            title="Hello World",                 # Title: human readable title of the post
            slug="hello-world",                  # Slug: URL-friendly unique identifier
            content="First content",             # Content: main body
            author=author,                       # Author: FK to User
        )

        # Basic existence and type checks
        self.assertIsNotNone(post.id, "Post should be saved and have a primary key.")
        self.assertEqual(post.title, "Hello World", "Title should be stored as given.")
        self.assertEqual(post.slug, "hello-world", "Slug should be stored as given.")
        self.assertEqual(post.content, "First content", "Content should be stored as given.")
        self.assertEqual(post.author, author, "Author FK should point to the user we created.")

        # Auto timestamps should be set after save
        self.assertIsNotNone(post.created_at, "created_at should be auto-populated.")
        self.assertIsNotNone(post.updated_at, "updated_at should be auto-populated.")

        # updated_at should be >= created_at (usually greater, but safe check)
        self.assertGreaterEqual(
            post.updated_at, 
            post.created_at, 
            "updated_at should not be earlier than created_at."
        )

    def test_post_str_returns_title(self):
        """
        The __str__ of Post should return its title for readable admin lists, logs, etc.
        """
        Post = self.get_post_model()
        author = self.create_user()

        post = Post.objects.create(
            title="Readable Title",
            slug="readable-title",
            content="x",
            author=author,
        )

        self.assertEqual(str(post), "Readable Title", "__str__ should return the title.")

    def test_slug_is_unique(self):
        """
        Slug should be unique to avoid URL collisions.
        Creating two posts with the same slug should raise IntegrityError.
        """
        Post = self.get_post_model()
        author = self.create_user()

        # Create first post with a specific slug
        Post.objects.create(
            title="First Post",
            slug="same-slug",
            content="Content A",
            author=author,
        )

        # Attempt to create second post with the same slug - should fail
        with self.assertRaises(
            IntegrityError, 
            msg="Expected IntegrityError when creating a Post with duplicate slug."
        ):
            Post.objects.create(
                title="Second Post",
                slug="same-slug",                # Duplicate slug
                content="Content B",
                author=author,
            )

    def test_updated_at_changes_on_modification(self):
        """
        The updated_at field should change when the post is modified.
        """
        Post = self.get_post_model()
        author = self.create_user()

        # Create initial post
        post = Post.objects.create(
            title="Original Title",
            slug="original-slug",
            content="Original content",
            author=author,
        )

        original_updated_at = post.updated_at

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        # Modify and save the post
        post.title = "Modified Title"
        post.save()

        # Refresh from database to get updated timestamp
        post.refresh_from_db()

        self.assertGreater(
            post.updated_at, 
            original_updated_at, 
            "updated_at should change when post is modified."
        )

    def test_post_author_relationship(self):
        """
        Test that the author relationship works correctly and can be accessed.
        """
        Post = self.get_post_model()
        author = self.create_user(email="testauthor@example.com")

        post = Post.objects.create(
            title="Author Test Post",
            slug="author-test-post",
            content="Testing author relationship",
            author=author,
        )

        # Test forward relationship (post -> author)
        self.assertEqual(
            post.author.email, 
            "testauthor@example.com", 
            "Should be able to access author from post."
        )
        self.assertEqual(
            post.author.username, 
            "testauthor@example.com", 
            "Author username should match."
        )

        # Test reverse relationship (author -> posts)
        author_posts = author.posts.all()
        self.assertIn(post, author_posts, "Post should be accessible from author's posts.")
        self.assertEqual(author_posts.count(), 1, "Author should have exactly one post.")