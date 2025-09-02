# posts/models.py
# Implements the Post model as described by the tests.

from django.db import models                       # Base ORM fields and model classes
from django.conf import settings                   # Access to project settings (AUTH_USER_MODEL)


class Post(models.Model):
    """
    Represents a blog post published on the site.
    
    Fields:
      - title: short, human-readable title for the post
      - slug: URL-friendly identifier (must be unique site-wide)
      - content: the main body text of the post
      - created_at: timestamp automatically set when the record is created
      - updated_at: timestamp automatically updated on each save
      - author: the user who wrote the post (ForeignKey to the active User model)
    
    Using settings.AUTH_USER_MODEL keeps it flexible if we switch to a custom user model later.
    """
    
    # Title: use CharField with a reasonable maximum length (200 is typical for titles)
    title = models.CharField(max_length=200)
    
    # Slug: must be unique to avoid URL collisions; allows only letters, numbers, hyphens/underscores
    slug = models.SlugField(max_length=220, unique=True)
    
    # Content: the main body of the article (TextField has no length limit in practice)
    content = models.TextField()
    
    # Timestamps: created_at set once at creation time; updated_at updated on every save
    created_at = models.DateTimeField(auto_now_add=True)  # auto_now_add sets the field on first save only
    updated_at = models.DateTimeField(auto_now=True)      # auto_now sets the field to now() on every save
    
    # Author: reference to the User who owns this post
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,        # Points to the configured user model (default 'auth.User')
        on_delete=models.CASCADE,        # If the user is deleted, their posts are deleted too
        related_name="posts",            # Allows reverse lookup like user.posts.all()
    )

    class Meta:
        # Default ordering: newest first (by creation time descending)
        ordering = ["-created_at"]
        # An index on 'slug' is created automatically for unique fields,
        # but if you needed compound indexes, you'd add them here via indexes = [...]

    def __str__(self) -> str:
        """
        Return the title for readable representations (admin lists, logs, etc.).
        """
        return self.title