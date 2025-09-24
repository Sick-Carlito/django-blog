# posts/models.py
# Models for the posts app: Category and Post (Post likely already exists).
from django.db import models                         # Django model base
from django.conf import settings                     # access AUTH_USER_MODEL
from django.urls import reverse                       # optional helper for get_absolute_url
from django.utils.text import slugify                 # helper if you auto-slug (optional)


class Category(models.Model):
    """
    Category model for grouping posts.
    - name: human readable category name
    - slug: URL-friendly unique identifier for the category
    - description: optional text
    """
    name = models.CharField(max_length=100, unique=True)
    # slug used in URLs; unique to allow reverse lookups like /category/<slug>/
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]  # alphabetical by name

    def __str__(self):
        """
        Return a readable representation used in admin and debugging.
        """
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided.
        """
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Optional: return a URL for the category detail page.
        Adjust the reverse target to your URL naming if you implement a detail view.
        """
        return reverse("posts:category-detail", kwargs={"slug": self.slug})


class Post(models.Model):
    """
    Post model — add categories as a many-to-many relationship.
    (If Post already exists in your code, add only the categories field.)
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    categories = models.ManyToManyField(Category, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NEW: many-to-many relation to Category.
    # - blank=True allows posts without categories
    # - related_name='posts' enables Category.posts.all() reverse lookup
    categories = models.ManyToManyField(
        Category, related_name="posts", blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return the detail URL for the Post (adjust name if different).
        """
        return reverse("posts:post-detail", kwargs={"slug": self.slug})
