# blog_project/urls.py
"""Top-level URL configuration for the project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),                 # includes accounts:register
    # Add Django's built-in authentication URLs (login/logout/password)
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("posts.urls", namespace="posts")),     # Include posts app URLs at the site root
]

# During local development (DEBUG=True) serve media files from MEDIA_URL
# This should NOT be used in production — production servers serve media from S3/CDN.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
