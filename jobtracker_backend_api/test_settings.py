import os
from datetime import timedelta

from .settings import *

# ==================== CORE DJANGO SETTINGS ====================

# Required settings for testing
SECRET_KEY = "test-secret-key-for-testing-only-do-not-use-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1", "testserver"]

# Use SQLite in-memory database for testing (fast and isolated)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {
            "NAME": ":memory:",
        },
    }
}

# ==================== GOOGLE API SETTINGS ====================

# Mock Google API credentials for testing
GOOGLE_API_CLIENT_ID = "test-google-client-id"
GOOGLE_API_CLIENT_SECRET = "test-google-client-secret"
GOOGLE_API_REDIRECT_URI = "http://localhost:8000/auth/google/callback/"

# ==================== JWT SETTINGS ====================

# Simple JWT configuration for testing
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": SECRET_KEY,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_COOKIE": "access_token",
    "AUTH_COOKIE_SECURE": False,  # False for testing
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SAMESITE": "Lax",
}

# ==================== CELERY SETTINGS ====================

# Make Celery run synchronously during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# ==================== EMAIL SETTINGS ====================

# Use in-memory email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ==================== LOGGING ====================

# Suppress logs during testing (optional)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",  # Only show warnings and errors
    },
}

# ==================== CACHING ====================

# Use dummy cache for testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# ==================== CORS SETTINGS ====================

# Allow all origins during testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ==================== TEST-SPECIFIC SETTINGS ====================


# Disable migrations for faster testing (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# Uncomment the line below if you want to disable migrations during testing
# MIGRATION_MODULES = DisableMigrations()

# ==================== CSRF SETTINGS ====================

# Fix CSRF_TRUSTED_ORIGINS for Django 4.0+
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://testserver",
]

# ==================== SECURITY SETTINGS ====================

# Disable some security features for testing
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ==================== MEDIA/STATIC FILES ====================

# Use temporary directories for media and static files during testing
import tempfile

MEDIA_ROOT = tempfile.mkdtemp()
STATIC_ROOT = tempfile.mkdtemp()

# ==================== INSTALLED APPS ====================

# You can override INSTALLED_APPS if needed for testing
# For example, to add test-specific apps or remove production-only apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "jobtracker_backend_api.service_provider",
    # Add any test-specific apps here if needed
]

# ==================== REST FRAMEWORK SETTINGS ====================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# ==================== OVERRIDE ANY OTHER SETTINGS ====================

# Add any other settings you need to override for testing
# For example, if you have custom middleware or other configurations

print("Using test settings for Django tests")
