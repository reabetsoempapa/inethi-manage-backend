"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path

from django.utils import timezone
import environ

env = environ.Env(
    DEBUG=(bool, False),
    SYNC_RD=(bool, False),
    SYNC_UNIFI=(bool, False),
    REDIS_HOST=(str, "localhost"),
    ALLOWED_HOSTS=(list, [])
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "manage.inethicloud.net",
    "manage.inethilocal.net",
    "manage-backend.inethilocal.net",
    "manage-backend.inethicloud.net",
] + env("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "https://manage.inethilocal.net",
    "https://manage.inethicloud.net",
    "https://manage-backend.inethilocal.net",
    "https://manage-backend.inethicloud.net",
]

# CORS settings for development. For production, consider specifying CORS_ALLOWED_ORIGINS.
CORS_ALLOW_ALL_ORIGINS = DEBUG  # For development

CORS_ALLOW_CREDENTIALS = True
# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_keycloak",
    "revproxy",
    "accounts",
    "monitoring",
    "metrics",
    "payments",
    "wallet",
    "sync",
    "radius",
]
# Keycloak config
AUTHENTICATION_BACKENDS = ["django_keycloak.backends.KeycloakAuthorizationCodeBackend"]
LOGIN_URL = "keycloak_login"
KEYCLOAK_CLIENTS = {
    "DEFAULT": {
        "URL": env("KEYCLOAK_URL"),
        "REALM": env("KEYCLOAK_REALM"),
        "CLIENT_ID": env("KEYCLOAK_CLIENT_ID"),
        "CLIENT_SECRET": env("KEYCLOAK_CLIENT_SECRET"),
    },
    "API": {
        "URL": env("KEYCLOAK_URL"),
        "REALM": env("KEYCLOAK_REALM"),
        "CLIENT_ID": env("DRF_KEYCLOAK_CLIENT_ID"),
        "CLIENT_SECRET": None,  # DRF client is public
    },
}
# Radiusdesk config
SYNC_RD_ENABLED = env("SYNC_RD")
RADIUSDESK_DB = env.db_url("RADIUSDESK_DB_URL")
RD_URL = env("RADIUSDESK_URL")
# UNIFI config
SYNC_UNIFI_ENABLED = env("SYNC_UNIFI")
UNIFI_DB_USER = ""
UNIFI_DB_PASSWORD = ""
UNIFI_DB_HOST = "localhost"
UNIFI_DB_PORT = "27117"
UNIFI_URL = env("UNIFI_URL")

# Nothing at the moment
MESH_SETTINGS_DEFAULTS = {}

WALLET_ENCRYPTION_KEY = env("WALLET_ENCRYPTION_KEY")
WALLET_CONTRACT_ADDRESS = env("WALLET_CONTRACT_ADDRESS")

DEVICE_CHECKS = [
    {
        "title": "CPU Usage",
        "key": "cpu",
        "setting": "check_cpu",
        "func": lambda v, s: v < s,
        "feedback": {
            "NO_DATA": "No CPU usage recorded",
            "NO_SETTING": "No CPU warning set",
            False: "CPU usage is high",
            True: "CPU usage falls in an acceptable range",
        },
    },
    {
        "title": "Memory Usage",
        "key": "mem",
        "setting": "check_mem",
        "func": lambda v, s: v < s,
        "feedback": {
            "NO_DATA": "No memory usage recorded",
            "NO_SETTING": "No memory warning set",
            False: "Memory usage is high",
            True: "Memory usage falls in an acceptable range",
        },
    },
    {
        "title": "Recently Contacted",
        "key": "last_ping",
        "setting": "check_ping",
        "func": lambda v, s: timezone.now() - v < s,
        "feedback": {
            "NO_DATA": "Device has never been pinged",
            "NO_SETTING": "No contact time warning set",
            False: "Device has not been pinged recently",
            True: "Device has been pinged recently",
        },
    },
    {
        "title": "Active",
        "key": "last_contact",
        "setting": "check_active",
        "func": lambda v, s: timezone.now() - v < s,
        "feedback": {
            "NO_DATA": "Device has not contacted the server",
            "NO_SETTING": "No active time warning set",
            False: "Device has not been contacted the server recently",
            True: "Device is active",
        },
    },
    {
        "title": "RTT",
        "key": "rtt",
        "setting": "check_rtt",
        "func": lambda v, s: v < s,
        "feedback": {
            "NO_DATA": "No RTT data",
            "NO_SETTING": "No RTT warning set",
            False: "Took too long to return a response",
            True: "Response time is acceptable",
        },
    },
    {
        "title": "Upload Speed",
        "key": "upload_speed",
        "setting": "check_upload_speed",
        "func": lambda v, s: v > s,
        "feedback": {
            "NO_DATA": "No upload speed data",
            "NO_SETTING": "No upload warning set",
            False: "Node is uploading data too slowly",
            True: "Upload speed is acceptable",
        },
    },
    {
        "title": "Download Speed",
        "key": "download_speed",
        "setting": "check_download_speed",
        "func": lambda v, s: v > s,
        "feedback": {
            "NO_DATA": "No download speed data",
            "NO_SETTING": "No download warning set",
            False: "Node is downloading data too slowly",
            True: "Download speed is acceptable",
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "django_keycloak.authentication.KeycloakDRFAuthentication",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

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

ASGI_APPLICATION = "backend.asgi.application"
WSGI_APPLICATION = "backend.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": env.db("DATABASE_URL"),
    "metrics_db": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "metrics.sqlite3",
    },
    "radius_db": RADIUSDESK_DB,
}

DATABASE_ROUTERS = ["backend.routers.MetricsRouter"]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Johannesburg"

USE_I18N = True

USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery config
REDIS_HOST = env("REDIS_HOST")
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:6379/0"
# Celery TIME_ZONE should be equal to django TIME_ZONE
# In order to schedule run_iperf3_checks on the correct time intervals
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = False

# Channels config
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://{REDIS_HOST}/1"],
        },
    },
}

CELERY_BEAT_SCHEDULE = {
    "ping_schedule": {
        "task": "metrics.tasks.run_pings",
        # Executes ping every 5 min
        "schedule": timedelta(minutes=5),
    },
    "sync_schedule": {
        "task": "sync.tasks.sync_dbs",
        # Executes db sync every hour
        "schedule": timedelta(minutes=60),
    },
    "alerts_schedule": {
        "task": "sync.tasks.generate_alerts",
        # Executes alert generation every 10 mins
        "schedule": timedelta(minutes=10),
    },
    "aggregate_hourly": {
        "task": "metrics.tasks.aggregate_all_hourly_metrics",
        "schedule": timedelta(hours=1),
    },
    "aggregate_daily": {
        "task": "metrics.tasks.aggregate_all_daily_metrics",
        "schedule": timedelta(days=1),
    },
    "aggregate_monthly": {
        "task": "metrics.tasks.aggregate_all_monthly_metrics",
        "schedule": timedelta(days=30),
    },
}

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
        "report": {
            "format": "{asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console_info": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",  # Use standard output rather than standard error
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "django_errors.log",
            "formatter": "verbose",
        },
        "reports_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "reports.log",
            "formatter": "report",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console_info", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console_info", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "general": {
            "handlers": ["console_info", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "reports": {
            "handlers": ["reports_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
