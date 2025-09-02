# posts/admin.py
# Register Post in Django admin to create/edit posts via the admin UI.

from django.contrib import admin         # Admin site registration utilities
from .models import Post                 # Import the Post model we created


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Customizes how Post appears in the admin list and edit pages.
    """
    list_display = ("title", "slug", "author", "created_at", "updated_at")  # Columns in list view
    list_filter = ("author", "created_at")                                   # Sidebar filters
    search_fields = ("title", "content", "slug")                             # Searchable fields
    prepopulated_fields = {"slug": ("title",)}                               # Auto-fill slug from title (optional)
