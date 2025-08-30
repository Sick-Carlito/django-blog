# blog_project/settings/prod.py
"""
Production settings — import from base and override for production behavior.
Make sure the .env contains secure values (SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS).
"""

from .base import *  # noqa: F401,F403

# Do not run with DEBUG True in production.
DEBUG = False

# ALLOWED_HOSTS should be read from environment for safety (e.g., "example.com,www.example.com")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Production database should be provided via DATABASE_URL environment variable, e.g.:
# DATABASE_URL=postgres://user:pass@host:port/dbname
DATABASES = {"default": env.db("DATABASE_URL")}

# Security-related headers and cookies for production
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
