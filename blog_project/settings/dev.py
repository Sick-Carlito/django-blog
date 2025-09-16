# blog_project/settings/dev.py
"""
Development settings — import everything from base and override safe defaults for local dev.
"""

from .base import *  # noqa: F401,F403  (import all base settings into the local namespace)

# For local dev we want DEBUG True so we get helpful tracebacks & auto-reload
DEBUG = True

# Allow localhost addresses while developing locally
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Use the console email backend for dev so emails are printed to terminal rather than sent
#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Use in-memory email backend for development & tests so emails are captured in django.core.mail.outbox
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optionally add development-specific apps (debug toolbar etc.) here:
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

# Where to redirect after successful login
LOGIN_REDIRECT_URL = "/"
# Where to redirect after logout
LOGOUT_REDIRECT_URL = "/"
# Login page (for LoginRequiredMixin and other redirects)
#LOGIN_URL = "/accounts/login/"

# Media files (user-uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')