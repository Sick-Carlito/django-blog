# posts/admin.py
from django.contrib import admin
from .models import Post, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # show name and slug in list view and enable search
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # show key fields in admin list view
    list_display = ("title", "author", "created_at")
    prepopulated_fields = {"slug": ("title",)}  # auto-fill slug from title in admin
    search_fields = ("title", "content", "author__username")
    # allow selecting many-to-many categories in the admin list form
    filter_horizontal = ("categories",)
