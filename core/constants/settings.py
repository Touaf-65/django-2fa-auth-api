"""
Constantes de configuration pour l'application Core
"""

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache
CACHE_TIMEOUT = 300  # 5 minutes
CACHE_LONG_TIMEOUT = 3600  # 1 heure
CACHE_SHORT_TIMEOUT = 60  # 1 minute

# Rate Limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 heure
RATE_LIMIT_BURST = 10

# Passwords
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SYMBOLS = True

# Usernames
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
USERNAME_ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-'

# Email
EMAIL_MAX_LENGTH = 254
EMAIL_VERIFICATION_REQUIRED = True
EMAIL_VERIFICATION_TIMEOUT = 86400  # 24 heures

# Phone
PHONE_MAX_LENGTH = 20
PHONE_VERIFICATION_REQUIRED = False
PHONE_VERIFICATION_TIMEOUT = 300  # 5 minutes

# Files
FILE_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_ALLOWED_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Images
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
    '.txt', '.csv', '.json', '.xml', '.yaml', '.yml',  # Text
    '.zip', '.rar', '.7z', '.tar', '.gz',  # Archives
    '.mp3', '.wav', '.flac', '.aac',  # Audio
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',  # Video
]

# Images
IMAGE_MAX_DIMENSIONS = (2000, 2000)
IMAGE_MIN_DIMENSIONS = (100, 100)
IMAGE_ALLOWED_FORMATS = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
IMAGE_QUALITY = 85

# Tokens
TOKEN_LENGTH = 32
TOKEN_EXPIRY = 3600  # 1 heure
REFRESH_TOKEN_LENGTH = 64
REFRESH_TOKEN_EXPIRY = 2592000  # 30 jours

# OTP
OTP_LENGTH = 6
OTP_EXPIRY = 300  # 5 minutes
OTP_MAX_ATTEMPTS = 3

# Sessions
SESSION_TIMEOUT = 1800  # 30 minutes
SESSION_EXTEND_ON_ACTIVITY = True
SESSION_MAX_AGE = 86400  # 24 heures

# Password Reset
PASSWORD_RESET_TIMEOUT = 3600  # 1 heure
PASSWORD_RESET_MAX_ATTEMPTS = 3

# Email Verification
EMAIL_VERIFICATION_TIMEOUT = 86400  # 24 heures
EMAIL_VERIFICATION_MAX_ATTEMPTS = 3

# 2FA
TOTP_ISSUER_NAME = "Django 2FA Auth API"
TOTP_WINDOW = 1
TOTP_DIGITS = 6
TOTP_PERIOD = 30

# Security
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes
IP_BLOCK_TIMEOUT = 3600  # 1 heure
SECURITY_EVENT_RETENTION_DAYS = 90

# Notifications
NOTIFICATION_RETENTION_DAYS = 30
NOTIFICATION_BATCH_SIZE = 100
NOTIFICATION_RATE_LIMIT = 1000  # par heure

# Permissions
PERMISSION_CACHE_TIMEOUT = 300  # 5 minutes
ROLE_CACHE_TIMEOUT = 600  # 10 minutes
GROUP_CACHE_TIMEOUT = 600  # 10 minutes

# API
API_VERSION = "1.0.0"
API_RATE_LIMIT = 1000  # par heure
API_TIMEOUT = 30  # secondes

# Database
DB_CONNECTION_TIMEOUT = 30
DB_QUERY_TIMEOUT = 60
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5

# Monitoring
METRICS_ENABLED = True
METRICS_INTERVAL = 60  # secondes
HEALTH_CHECK_TIMEOUT = 5  # secondes

# External Services
SENDGRID_API_KEY = None
SENDGRID_FROM_EMAIL = None
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TWILIO_FROM_PHONE = None
FIREBASE_SERVER_KEY = None

# Social Auth
GOOGLE_CLIENT_ID = None
GOOGLE_CLIENT_SECRET = None
FACEBOOK_APP_ID = None
FACEBOOK_APP_SECRET = None
TWITTER_API_KEY = None
TWITTER_API_SECRET = None
LINKEDIN_CLIENT_ID = None
LINKEDIN_CLIENT_SECRET = None

# Storage
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = "media"
MEDIA_URL = "/media/"
STATIC_ROOT = "static"
STATIC_URL = "/static/"

# Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_TIMEOUT = 5

# Elasticsearch
ELASTICSEARCH_HOSTS = ["localhost:9200"]
ELASTICSEARCH_INDEX_PREFIX = "django_2fa_auth"
ELASTICSEARCH_TIMEOUT = 30

# AWS
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_STORAGE_BUCKET_NAME = None
AWS_S3_REGION_NAME = "us-east-1"
AWS_S3_CUSTOM_DOMAIN = None
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

# Google Cloud
GOOGLE_CLOUD_PROJECT_ID = None
GOOGLE_CLOUD_STORAGE_BUCKET = None
GOOGLE_CLOUD_CREDENTIALS_FILE = None

# Azure
AZURE_ACCOUNT_NAME = None
AZURE_ACCOUNT_KEY = None
AZURE_CONTAINER = None

# Email Backends
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
EMAIL_TIMEOUT = 30

# SMS Backends
SMS_BACKEND = "core.sms.backends.twilio.TwilioBackend"
SMS_DEFAULT_FROM = None

# Push Notification Backends
PUSH_BACKEND = "core.push.backends.fcm.FCMBackend"
PUSH_DEFAULT_TOPIC = "general"

# Webhook
WEBHOOK_TIMEOUT = 30
WEBHOOK_MAX_RETRIES = 3
WEBHOOK_RETRY_DELAY = 5

# Backup
BACKUP_ENABLED = True
BACKUP_SCHEDULE = "0 2 * * *"  # Tous les jours à 2h
BACKUP_RETENTION_DAYS = 30
BACKUP_COMPRESSION = True

# Maintenance
MAINTENANCE_MODE = False
MAINTENANCE_MESSAGE = "Le système est en maintenance. Veuillez réessayer plus tard."
MAINTENANCE_ALLOWED_IPS = []

# Development
DEBUG = False
DEBUG_TOOLBAR = False
DEBUG_SQL = False
DEBUG_TEMPLATES = False

# Testing
TEST_RUNNER = "django.test.runner.DiscoverRunner"
TEST_DATABASE_PREFIX = "test_"
TEST_MEDIA_ROOT = "test_media"

# Performance
USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = []
CORS_ALLOWED_HEADERS = [
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
CORS_ALLOWED_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# CSRF
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = []

# Session
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 1209600  # 2 semaines
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CULL_FREQUENCY": 3,
        },
    }
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
        "OPTIONS": {
            "timeout": 30,
        },
    }
}

# Internationalization
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
    ("es", "Español"),
    ("de", "Deutsch"),
    ("it", "Italiano"),
    ("pt", "Português"),
    ("ru", "Русский"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("ar", "العربية"),
    ("hi", "हिन्दी"),
]

LOCALE_PATHS = [
    "locale",
]

# Static Files
STATICFILES_DIRS = [
    "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media Files
MEDIA_ROOT = "media"
MEDIA_URL = "/media/"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
            ],
        },
    },
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

# Installed Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "drf_spectacular",
    "core",
    "apps.authentication",
    "apps.users",
    "apps.notifications",
    "apps.security",
    "apps.permissions",
]

# REST Framework
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
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": DEFAULT_PAGE_SIZE,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": 3600,  # 1 heure
    "REFRESH_TOKEN_LIFETIME": 2592000,  # 30 jours
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": None,  # Sera défini dans les settings
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": 3600,
    "SLIDING_TOKEN_REFRESH_LIFETIME": 2592000,
}

# Spectacular (OpenAPI)
SPECTACULAR_SETTINGS = {
    "TITLE": "Django 2FA Auth API",
    "DESCRIPTION": "API complète pour l'authentification Django avec 2FA, gestion des utilisateurs, notifications, sécurité et système de permissions avancé.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SCHEMA_PATH_PREFIX": "/api/",
    "TAGS": [
        {"name": "Authentication", "description": "Authentification et 2FA"},
        {"name": "Users", "description": "Gestion des utilisateurs et profils"},
        {"name": "Notifications", "description": "Système de notifications"},
        {"name": "Security", "description": "Sécurité et monitoring"},
        {"name": "Permissions", "description": "Système de permissions avancé"},
    ],
    "EXTENSIONS_INFO": {
        "x-logo": {
            "url": "https://www.djangoproject.com/s/img/logos/django-logo-positive.png",
            "altText": "Django Logo",
        }
    },
    "CONTACT": {
        "name": "API Support",
        "email": "support@example.com",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "SERVERS": [
        {
            "url": "http://localhost:8000",
            "description": "Serveur de développement",
        },
        {
            "url": "https://api.example.com",
            "description": "Serveur de production",
        }
    ],
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "PERMISSION_WHITELIST": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums"
    ],
    "PREPROCESSING_HOOKS": [
        "drf_spectacular.hooks.preprocess_exclude_path_format"
    ],
    "SORT_OPERATIONS": True,
    "SORT_TAGS": True,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "GENERIC_ADDITIONAL_PROPERTIES": None,
    "DISABLE_ERRORS_AND_WARNINGS": False,
    "ENABLE_DJANGO_DEPLOY_CHECK": False,
    "CUSTOM_UI_DIST": None,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tryItOutEnabled": True,
    },
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
        "expandResponses": "200,201",
        "pathInMiddlePanel": True,
        "theme": {
            "colors": {
                "primary": {
                    "main": "#1976d2"
                }
            }
        }
    }
}



