# posts/tests/test_crud_flow.py
# Integrated CRUD flow tests using django.test.TestCase to simulate browser actions.
#
# We exercise:
#  - Create (POST to post-create) as staff (staff users create posts)
#  - Read (list and detail pages show created post)
#  - Update (author updates their post)
#  - Delete (author deletes their post)
#  - Non-author is forbidden to update or delete
#
# These tests use the Django test client to simulate browser requests.
# Run with: python manage.py test posts.tests.test_crud_flow

from django.test import TestCase, Client
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import get_user_model

class CRUDFlowTests(TestCase):
    """
    TestCase for end-to-end CRUD flows:
      - staff user creates a post (Create)
      - everyone can read (List & Detail)
      - author edits their post (Update)
      - author deletes their post (Delete)
      - non-author cannot edit or delete (403)
    """

    def setUp(self):
        """
        Create three users and initialize a test client:
        - staff_user: is_staff=True (will create the post)
        - other_user: regular user (cannot update/delete others' posts)
        - author_user: will be the author after creation (same as staff in this flow)
        """
        User = get_user_model()                 # fetch active user model

        # Create a staff user who will create the post (and therefore be its author)
        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="staffpass123"
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

        # Create a different normal user (non-author)
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )

        # We will treat staff_user as the author (no separate 'author_user' needed)
        self.client = Client()                  # test client simulates browser requests

    def test_full_crud_flow_as_staff_author(self):
        """
        1) Staff (author) creates a post via POST to 'posts:post-create'
        2) List view shows that post
        3) Detail view shows that post content
        4) Author updates the post via POST to 'posts:post-update'
        5) Updated content appears on detail view
        6) Author deletes the post via POST to 'posts:post-delete'
        7) Post is removed from DB and list no longer shows it
        """
        Post = apps.get_model("posts", "Post")   # get the Post model

        # --- 1) Create a post as staff user (login first)
        login_ok = self.client.login(username="staffuser", password="staffpass123")
        self.assertTrue(login_ok, "Staff user should be able to login for create step.")

        create_url = reverse("posts:post-create")
        create_data = {
            "title": "CRUD Test Post",
            "slug": "crud-test-post",
            "content": "Initial content",
        }

        # POST the create form (follow redirects so we land on detail if redirected)
        create_response = self.client.post(create_url, create_data, follow=True)
        self.assertEqual(create_response.status_code, 200, "Create POST should result in successful redirect/follow.")

        # After creation, the Post should exist
        self.assertTrue(Post.objects.filter(slug="crud-test-post").exists(), "Post should be created in DB.")
        post = Post.objects.get(slug="crud-test-post")

        # Ensure the author of the post is the staff user who created it
        self.assertEqual(post.author.username, "staffuser", "Post author should be the creating staff user.")

        # --- 2) Read: list view should contain the post title
        list_url = reverse("posts:post-list")
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "CRUD Test Post", msg_prefix="List view should show created post title.")

        # --- 3) Read: detail view should show title and content
        detail_url = reverse("posts:post-detail", kwargs={"slug": post.slug})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "CRUD Test Post")
        self.assertContains(detail_response, "Initial content")

        # --- 4) Update: author (staff user) updates the post
        update_url = reverse("posts:post-update", kwargs={"slug": post.slug})
        update_data = {
            "title": "CRUD Test Post - Updated",
            "slug": post.slug,  # keep slug same for simplicity
            "content": "Updated content",
        }
        update_response = self.client.post(update_url, update_data, follow=True)
        self.assertEqual(update_response.status_code, 200, "Update POST should redirect and follow to 200.")

        # Refresh object from DB and assert updates applied
        post.refresh_from_db()
        self.assertEqual(post.title, "CRUD Test Post - Updated")
        self.assertEqual(post.content, "Updated content")

        # Confirm updated content shows on detail page
        detail_response_after = self.client.get(detail_url)
        self.assertContains(detail_response_after, "CRUD Test Post - Updated")
        self.assertContains(detail_response_after, "Updated content")

        # --- 5) Delete: author deletes the post via delete URL
        delete_url = reverse("posts:post-delete", kwargs={"slug": post.slug})
        delete_response = self.client.post(delete_url, follow=True)
        self.assertEqual(delete_response.status_code, 200, "Delete POST should redirect and follow to 200.")

        # Post should be removed from DB
        self.assertFalse(Post.objects.filter(slug="crud-test-post").exists(), "Post should be deleted.")

        # List view should no longer contain the post title
        list_response_after_delete = self.client.get(list_url)
        self.assertNotContains(list_response_after_delete, "CRUD Test Post - Updated")

    def test_non_author_cannot_update_or_delete(self):
        """
        Verify that a logged-in non-author cannot update or delete the post (403).
        Steps:
         - Staff creates the post
         - Logout and login as other_user
         - Attempts to GET update/delete -> receive 403 (or redirect then 403 for logged-in)
        """
        Post = apps.get_model("posts", "Post")

        # Login as staff and create a post (author = staffuser)
        self.client.login(username="staffuser", password="staffpass123")
        self.client.post(reverse("posts:post-create"), {
            "title": "Protected Post",
            "slug": "protected-post",
            "content": "Protected content",
        }, follow=True)
        post = Post.objects.get(slug="protected-post")
        self.client.logout()

        # Login as other_user (non-author)
        self.client.login(username="otheruser", password="otherpass123")

        # Attempt to GET update -> expect 403
        update_url = reverse("posts:post-update", kwargs={"slug": post.slug})
        update_get = self.client.get(update_url)
        self.assertEqual(update_get.status_code, 403, "Non-author should receive 403 on update GET.")

        # Attempt to GET delete -> expect 403
        delete_url = reverse("posts:post-delete", kwargs={"slug": post.slug})
        delete_get = self.client.get(delete_url)
        self.assertEqual(delete_get.status_code, 403, "Non-author should receive 403 on delete GET.")

