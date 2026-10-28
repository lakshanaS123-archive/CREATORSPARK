"""
Django settings for CreatorSpark project.

Generated for CreatorSpark — A modern content idea generation and planning
platform for Instagram influencers and social media creators.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from .env file if present
load_dotenv(BASE_DIR / '.env')

# Debug Mode (Defaults to True in local dev; set DEBUG=False or DJANGO_DEBUG=False in production)
DEBUG_RAW = os.getenv('DJANGO_DEBUG') if os.getenv('DJANGO_DEBUG') is not None else os.getenv('DEBUG', 'True')
DEBUG = DEBUG_RAW.lower() in ('true', '1', 'yes')

# SECRET KEY Configuration
# Reads either DJANGO_SECRET_KEY or SECRET_KEY from environment variables.
# When DEBUG=False, production MUST provide an explicit secret key.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or os.getenv('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-creatorspark-dev-local-key-stage1-foundation'
    else:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            "Production requires DJANGO_SECRET_KEY or SECRET_KEY environment variable to be set when DEBUG=False."
        )

# Host configuration (supports DJANGO_ALLOWED_HOSTS or ALLOWED_HOSTS)
ALLOWED_HOSTS_RAW = os.getenv('DJANGO_ALLOWED_HOSTS') or os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,0.0.0.0,testserver')
ALLOWED_HOSTS = [
    host.strip()
    for host in ALLOWED_HOSTS_RAW.split(',')
    if host.strip()
]

# Support Render external hostname automatically if present
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF Trusted Origins (supports DJANGO_CSRF_TRUSTED_ORIGINS or CSRF_TRUSTED_ORIGINS)
CSRF_ORIGINS_RAW = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS') or os.getenv('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1,http://localhost')
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in CSRF_ORIGINS_RAW.split(',')
    if origin.strip()
]

if RENDER_EXTERNAL_HOSTNAME:
    https_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if https_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(https_origin)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # CreatorSpark Core Application
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be right after SecurityMiddleware for static serving
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'creatorspark.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.creatorspark_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'creatorspark.wsgi.application'


# Database
# Uses SQLite for local development by default.
# Automatically detects and configures PostgreSQL when DATABASE_URL is set (e.g. on Render).
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for production static files compression and caching
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


# Media files (User uploads, reference media)
# https://docs.djangoproject.com/en/6.1/topics/files/

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload restrictions (Max 5MB for reference media)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB in bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB in bytes


# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'


# Security Settings for Production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
