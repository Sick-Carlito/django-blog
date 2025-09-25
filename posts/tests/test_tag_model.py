
# posts/tests/test_tag_model.py
# Tests for Tag model and the Post <-> Tag many-to-many relationship (TDD).
#
# Tests:
#  - Tag can be created (name & slug)
#  - Post model has a 'tags' many-to-many field
#  - Can attach Tag to Post and do reverse lookup
#  - Tag slug is auto-generated from name if not provided

from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Category, Tag  # Tag will be missing initially (RED)

class TagModelTests(TestCase):
    def setUp(self):
        # create a test user for post author
        User = get_user_model()                  # support custom user model
        self.user = User.objects.create_user(username="taguser", password="testpass")
        # create a sample post to attach tags to
        self.post = Post.objects.create(
            title="Tag Test Post",
            slug="tag-test-post",
            content="Testing tags",
            author=self.user,
        )

    def test_tag_create_and_slug(self):
        # Create a Tag with explicit slug
        t = Tag.objects.create(name="Django", slug="django")
        # Verify Tag saved
        self.assertTrue(Tag.objects.filter(slug="django").exists())

        # Create a Tag without slug and verify auto-slugging
        t2 = Tag.objects.create(name="Machine Learning")
        # slug should be auto-generated (lowercase, hyphenated)
        self.assertEqual(t2.slug, "machine-learning")

    def test_post_has_tags_m2m_field(self):
        # Ensure Post model has a many-to-many field 'tags'
        field = Post._meta.get_field("tags")
        self.assertTrue(field.many_to_many)

    def test_attach_tag_to_post_and_reverse_lookup(self):
        # Create two tags and attach to the post
        t1 = Tag.objects.create(name="Python", slug="python")
        t2 = Tag.objects.create(name="Web", slug="web")
        # add to post
        self.post.tags.add(t1, t2)
        # post should be in t1.posts and t2.posts
        self.assertIn(self.post, t1.posts.all())
        self.assertIn(t1, self.post.tags.all())
