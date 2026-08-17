"""
Django settings for Crime Reporting System
Production-ready with Supabase S3 Storage
Deployed on Render.com
"""

import os
import sys
from datetime import timedelta
from pathlib import Path
from decouple import config, Csv
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "storages",  # For S3 storage
    # Local apps
    "accounts",
    "reports",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Use PostgreSQL if DATABASE_URL is set (Render production)
if config("DATABASE_URL", default=None):
    DATABASES = {
        "default": dj_database_url.parse(
            config("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ============================================
# SUPABASE S3 STORAGE CONFIGURATION
# ============================================

# Supabase credentials
SUPABASE_URL = config("SUPABASE_URL", default="")
SUPABASE_KEY = config("SUPABASE_KEY", default="")
SUPABASE_SERVICE_KEY = config("SUPABASE_SERVICE_KEY", default="")
SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="crime-evidence")

# S3 Compatible Storage Settings (Supabase)
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="crime-evidence")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="")

# Check if all required credentials are present
USE_SUPABASE_STORAGE = all([
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_ENDPOINT_URL,
    SUPABASE_URL,
])

# ============================================
# STORAGE CONFIGURATION
# ============================================

if USE_SUPABASE_STORAGE:
    # AWS S3 Settings for boto3
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = False  # Don't add auth to URLs
    
    # Storage configuration
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    
    # Construct the media URL
    MEDIA_URL = f"{SUPABASE_URL}/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}/"
    
    print("=" * 60)
    print("✅ USING SUPABASE S3 STORAGE")
    print(f"   Bucket: {AWS_STORAGE_BUCKET_NAME}")
    print(f"   Region: {AWS_S3_REGION_NAME}")
    print(f"   Media URL: {MEDIA_URL}")
    print("=" * 60)
else:
    # Fallback to local file storage
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
    
    print("=" * 60)
    print("⚠️ USING LOCAL FILE STORAGE")
    print("   Supabase S3 not configured or missing credentials")
    print("=" * 60)

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================
# REST FRAMEWORK
# ============================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "120/minute",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

# ============================================
# JWT AUTHENTICATION
# ============================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=config("JWT_ACCESS_LIFETIME_MIN", default=60, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("JWT_REFRESH_LIFETIME_DAYS", default=7, cast=int)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# ============================================
# CORS CONFIGURATION
# ============================================

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:5173,http://localhost:3000", cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ============================================
# SECURITY (Production settings)
# ============================================

if not DEBUG:
    # SSL/HTTPS settings
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
    
    # Security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Referrer policy
    SECURE_REFERRER_POLICY = "same-origin"
    
    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "reports": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================
# EMAIL CONFIGURATION (Optional)
# ============================================

# For production, configure email settings if needed
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = config("EMAIL_HOST", default="")
# EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
# EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
# EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@crimesystem.com")

# ============================================
# ADMIN SITE CONFIGURATION
# ============================================

ADMIN_SITE_HEADER = "Crime Reporting System Admin"
ADMIN_SITE_TITLE = "Crime Reporting System"
ADMIN_INDEX_TITLE = "Dashboard"

# ============================================
# CELERY CONFIGURATION (Optional - for background tasks)
# ============================================

# CELERY_BROKER_URL = config("REDIS_URL", default="")
# CELERY_RESULT_BACKEND = config("REDIS_URL", default="")
# CELERY_ACCEPT_CONTENT = ["application/json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TIMEZONE = TIME_ZONE

# ============================================
# RATE LIMITING (Optional)
# ============================================

REST_FRAMEWORK.update({
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/minute",
    }
})

# ============================================
# API VERSIONING
# ============================================

REST_FRAMEWORK.update({
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "VERSION_PARAM": "version",
})

# ============================================
# CUSTOM SETTINGS
# ============================================

# Maximum file upload size (25MB)
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB in bytes

# Allowed file types for evidence
ALLOWED_EVIDENCE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "video/quicktime",
    "audio/mpeg",
    "audio/mp4",
    "application/pdf",
]

# Tracking code prefix
TRACKING_CODE_PREFIX = "CR"

# Emergency contact
EMERGENCY_PHONE = config("EMERGENCY_PHONE", default="+234 800 123 4567")
EMERGENCY_EMAIL = config("EMERGENCY_EMAIL", default="emergency@crimesystem.com")

# ============================================
# DEBUG TOOLBAR (Development only)
# ============================================

if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ["127.0.0.1"]
    except ImportError:
        pass