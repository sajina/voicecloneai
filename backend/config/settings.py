"""
Django settings for AI Voice Cloning application.
Optimized for deployment on Railway.app.
"""

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Force IPv4 on Railway (IPv6 is not available in Railway containers,
# causing "Network is unreachable" when connecting to smtp.gmail.com)
import socket
_original_getaddrinfo = socket.getaddrinfo

def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Force IPv4 by setting family to AF_INET when family is unspecified."""
    if family == 0:
        family = socket.AF_INET
    return _original_getaddrinfo(host, port, family, type, proto, flags)

if os.getenv('ENVIRONMENT') == 'production':
    socket.getaddrinfo = _ipv4_getaddrinfo

# Load environment variables from .env only in development
# In production, Railway injects them directly
load_dotenv()

# =============================================================================
# Core Settings
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# Railway sets ENVIRONMENT automatically, default to 'production' if not set
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DEBUG = ENVIRONMENT == 'development'

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]
# Railway automatically injects RAILWAY_PUBLIC_DOMAIN with the generated domain
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
# Always accept *.railway.app so domain regeneration never breaks the app
ALLOWED_HOSTS.append('.railway.app')
if DEBUG:
    ALLOWED_HOSTS = ['*']  # Allow all hosts in development

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# Application Definition
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # Local apps
    'apps.users',
    'apps.voices',
    'apps.payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serves static files efficiently
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# =============================================================================
# Database
# =============================================================================
# Railway provides a DATABASE_URL environment variable (usually PostgreSQL)
# If not set, fallback to SQLite for local testing (not recommended in production)
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('MYSQL_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local fallback – use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# =============================================================================
# Authentication
# =============================================================================

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =============================================================================
# Static & Media Files
# =============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# =============================================================================
# REST Framework
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}


# =============================================================================
# JWT
# =============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}


# =============================================================================
# CORS & CSRF
# =============================================================================

# In production, set CORS_ALLOWED_ORIGINS to your frontend domain(s)
# Helper to clean origins (remove paths/trailing slashes)
def clean_origin(url):
    url = url.strip()
    if not url: return ''
    try:
        from urllib.parse import urlparse
        p = urlparse(url)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}"
    except:
        pass
    return url.rstrip('/')

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [clean_origin(o) for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
    CORS_ALLOW_CREDENTIALS = True
    
    FRONTEND_URL = clean_origin(os.getenv('FRONTEND_URL', ''))
    if FRONTEND_URL and FRONTEND_URL not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)

CSRF_TRUSTED_ORIGINS = [clean_origin(o) for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
# Auto-add Railway public domain for CSRF
if RAILWAY_PUBLIC_DOMAIN:
    railway_origin = f'https://{RAILWAY_PUBLIC_DOMAIN}'
    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)


# =============================================================================
# Email
# =============================================================================

# In production (Railway), use Resend HTTP API since SMTP ports are blocked.
# In development, use regular Gmail SMTP.
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

if RESEND_API_KEY and not DEBUG:
    # Production: Resend HTTP API (no SMTP needed)
    EMAIL_BACKEND = 'config.email_backend.ResendEmailBackend'
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'VoiceAI <onboarding@resend.dev>')
else:
    # Development: Gmail SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    EMAIL_TIMEOUT = 30


# =============================================================================
# Security (Production)
# =============================================================================

if not DEBUG:
    # Security settings for HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Adjust SameSite for cross‑origin cookies if needed
    CSRF_COOKIE_SAMESITE = "None" if CORS_ALLOW_CREDENTIALS else "Lax"
    SESSION_COOKIE_SAMESITE = "None" if CORS_ALLOW_CREDENTIALS else "Lax"


# =============================================================================
# Logging (optional)
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}