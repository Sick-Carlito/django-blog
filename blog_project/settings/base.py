# blog_project/settings/base.py
"""
Base Django settings for the project.
Settings here are environment-agnostic and imported by dev.py / prod.py.
"""

from pathlib import Path   # Path for convenient filesystem paths
import os                  # os provides path joining and environment helpers
import environ             # django-environ: reads .env files and environment variables

# BASE_DIR — the project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize django-environ and read the .env file in the project root
# We declare a default type for DEBUG (bool) to help casting when reading env values.
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECRET_KEY is read from the .env file and kept out of source control
SECRET_KEY = env("SECRET_KEY")

# DEBUG default is False; dev.py will override to True for local work
DEBUG = env("DEBUG")

# ALLOWED_HOSTS read as a CSV list in the .env file (or use an empty list)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Application definition (core Django apps; extend this with your apps later)
INSTALLED_APPS = [
    "django.contrib.admin",        # Admin site
    "django.contrib.auth",         # Authentication system
    "django.contrib.contenttypes", # Content types framework
    "django.contrib.sessions",     # Session framework
    "django.contrib.messages",     # Messaging framework
    "django.contrib.staticfiles",  # Static files handling
    # Third-party & local apps will be appended later (e.g., 'blog', 'crispy_forms')
    "posts",
    "accounts",    # <- newly added accounts app
]

# Middleware stack runs on every request/response
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",               # Security headers
    "whitenoise.middleware.WhiteNoiseMiddleware",                 # Serves static files in production-ish setups
    "django.contrib.sessions.middleware.SessionMiddleware",       # Session cookie handling
    "django.middleware.common.CommonMiddleware",                  # Useful defaults like APPEND_SLASH
    "django.middleware.csrf.CsrfViewMiddleware",                  # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",    # Attaches user to request
    "django.contrib.messages.middleware.MessageMiddleware",       # Message framework
    "django.middleware.clickjacking.XFrameOptionsMiddleware",     # Clickjacking protection
]

# Root URL configuration module. The top-level URL router lives in blog_project/urls.py
ROOT_URLCONF = "blog_project.urls"

# Template configuration – where Django looks for HTML templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Search templates inside 'templates' directories of each app and at BASE_DIR / "templates"
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # Look for templates/ inside installed apps
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# WSGI application path; the callable used by WSGI servers
WSGI_APPLICATION = "blog_project.wsgi.application"

# Database: default reads DATABASE_URL from .env; fallback to SQLite in project root
DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Password validation (Django's recommended validators)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
# Directory where static files will be collected to (for production)
STATIC_ROOT = BASE_DIR / "staticfiles"
# Additional static sources for development
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files (user-uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redirect after successful login
LOGIN_REDIRECT_URL = "posts:post-list"
