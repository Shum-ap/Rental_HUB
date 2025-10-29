"""
Django settings for Rental HUB — unified and production-ready configuration.
"""

import os
import socket
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from decouple import Config, RepositoryEnv

# === Base project paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'users.User'

# === Environment detection ===
hostname = socket.gethostname()
if "prod" in hostname or "production" in hostname:
    env_file = ".env.prod"
elif "stage" in hostname or "staging" in hostname:
    env_file = ".env.staging"
else:
    env_file = ".env.dev"

env_file = os.getenv("ENV_FILE", env_file)
env_path = BASE_DIR / env_file
config = Config(RepositoryEnv(env_path))

# === Core Django settings ===
SECRET_KEY = config('SECRET_KEY', default='dev-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

CSRF_TRUSTED_ORIGINS = [
    f"http://{h}" for h in ALLOWED_HOSTS if h != '*'
] + [
    f"https://{h}" for h in ALLOWED_HOSTS if h != '*'
]

# === Installed Apps ===
INSTALLED_APPS = [
    # --- Django Core ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_extensions',
    'djcelery_email',
    'django_filters',
    'storages',

    'apps.core.apps.CoreConfig',
    'apps.listings.apps.ListingsConfig',
    'apps.reservations.apps.ReservationsConfig',
    'apps.feedbacks.apps.FeedbacksConfig',
    'apps.users.apps.UsersConfig',
    'apps.log.apps.LogConfig',
    'apps.transactions.apps.TransactionsConfig',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# === Database ===
db_engine = config('DB_ENGINE', default='sqlite')
if db_engine == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='rentalhub'),
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default='password'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
        }
    }

# === Password Validation ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Internationalization ===
LANGUAGES = [
    ('en', _('English')),
    ('de', _('German')),
    ('ru', _('Russian')),
]
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATETIME_FORMAT = "Y-m-d H:i"
DATE_FORMAT = "Y-m-d"
TIME_FORMAT = "H:i"
LOCALE_PATHS = [BASE_DIR / 'locale']
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000  # 1 year

# === Static & Media ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === AWS S3 Storage (for production) ===
USE_S3 = not DEBUG
if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='rentalhub-media')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-central-1')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# === REST Framework ===
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# === Caching ===
if DEBUG:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://redis:6379/1')
        }
    }

# === Celery ===
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
if DEBUG:
    CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=True, cast=bool)

# === Email ===
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.mailtrap.io')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = config('EMAIL_PORT', default=2525, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = 'noreply@rentalhub.com'
SERVER_EMAIL = 'admin@rentalhub.com'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# === Logging ===
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} — {name}: {message}", "style": "{"},
        "simple": {"format": "{levelname}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "file_general": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "general.log"),
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "file_views": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "views.log"),
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "file_errors": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "errors.log"),
            "level": "ERROR",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "file_general"], "level": "INFO", "propagate": True},
        "django.request": {"handlers": ["file_errors"], "level": "ERROR", "propagate": False},
        "log_views": {"handlers": ["console", "file_views"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["console", "file_general"], "level": "WARNING"},
}
