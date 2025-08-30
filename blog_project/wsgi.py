# blog_project/wsgi.py
"""
WSGI config for production deployments.

This file exposes the WSGI callable as a module-level variable named `application`.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings for the WSGI app (safe for hosting environments)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings.prod")

# Get the WSGI application for use by WSGI servers like Gunicorn or uWSGI
application = get_wsgi_application()
