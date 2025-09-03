# blog_project/urls.py
"""Top-level URL configuration for the project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),     # Include posts app URLs at the site root

    # Placeholder for the blog app routes. We will create "blog.urls" later.
    # For now, include an empty placeholder or point to Django's admin root.
    # path("", include("blog.urls")),
]

# During local development (DEBUG=True) serve media files from MEDIA_URL
# This should NOT be used in production — production servers serve media from S3/CDN.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
