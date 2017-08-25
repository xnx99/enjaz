"""
Django settings for enjaz project.

Generated by 'django-admin startproject' using Django 1.8.14.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib.messages import constants as messages
import secrets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secrets.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getattr(secrets, 'DEBUG', True)

ALLOWED_HOSTS = ['.enjazportal.com', '127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rules',
    'accounts',
    'approvals',
>>>>>>> f062ad443ce68e15372fd3484ad3b2cf375ad22b
    'activities',
    'activities2',
    'api',
    'bootstrap3',
    'bulb',
    'certificates',
    'clubs',
    'constance',
    'constance.backends.database',
    'core',
    'corsheaders',
    'easy_thumbnails',
    'events',
    'forms_builder.forms',
    'forms_builder.wrapper',
    'guardian',
    'loginas',
    'hpc',
    'media',
    'niqati',
    'post_office',
    'questions',
    'researchhub',
    'rest_framework',
    'rest_framework.authtoken',
    'social.apps.django_app.default',
    'studentguide',
    'studentvoice',
    'tagging',
    'tagging_autocomplete',
    'teams',
    'tedx',
    'userena',
    'wkhtmltopdf',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'enjaz.urls'

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
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'enjaz.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DEFAULT_DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
DATABASES = getattr(secrets, 'DATABASES', DEFAULT_DATABASES)

# Internationalization
LANGUAGE_CODE = 'ar-SA'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ= True

STATIC_URL = getattr(secrets, 'STATIC_URL', '/static/')
DEFAULT_STATIC_ROOT = os.path.join(BASE_DIR, 'static_files/')
if DEBUG:
    STATICFILES_DIRS = (DEFAULT_STATIC_ROOT,)
else:
    STATIC_ROOT = getattr(secrets, 'STATIC_ROOT', DEFAULT_STATIC_ROOT)

MEDIA_URL = getattr(secrets, 'MEDIA_URL', '/media/')
DEFAULT_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files/')
MEDIA_ROOT = getattr(secrets, 'MEDIA_ROOT', DEFAULT_MEDIA_ROOT)

# Email settings
EMAIL_USE_TLS = getattr(secrets, 'EMAIL_USE_TLS', None)
EMAIL_HOST = getattr(secrets, 'EMAIL_HOST', None)
EMAIL_PORT = getattr(secrets, 'EMAIL_PORT', None)
EMAIL_HOST_USER = getattr(secrets, 'EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = getattr(secrets, 'EMAIL_HOST_PASSWORD', None)
DEFAULT_FROM_EMAIL = 'noreply@enjazportal.com'
SERVER_EMAIL = 'errors@enjazportal.com'
EMAIL_BACKEND = getattr(secrets, "EMAIL_BACKEND", "django.core.mail.backends.dummy.EmailBackend")
ADMINS = [('Errors', 'errors@enjazportal.com')]


# Userena settings
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)
SITE_ID = 1
ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'accounts.EnjazProfile'
LOGIN_URL = '/accounts/signin/'
LOGIN_REDIRECT_URL = '/'
USERENA_SIGNIN_REDIRECT_URL = '/'
USERENA_REDIRECT_ON_SIGNOUT = '/'
LOGOUT_URL = '/accounts/signout/'
LOGOUT_REDIRECT_URL = '/'
USERENA_WITHOUT_USERNAMES = True
USERENA_ACTIVATION_RETRY = True
USERENA_ACTIVATION_DAYS = 30

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}


# Form app settings

FORMS_BUILDER_USE_SLUGS = False
FORMS_BUILDER_USE_SITES = False
FORMS_BUILDER_CHOICES_SEPARATOR = '/'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'STUDENTVOICE_THRESHOLD': (30, 'What is the point threshold on which voices should be sent to their recipients?'),
    'DEBATE_URL': ('',''),
}


# External API keys
SOCIAL_AUTH_TWITTER_KEY = getattr(secrets, "SOCIAL_AUTH_TWITTER_KEY", "")
SOCIAL_AUTH_TWITTER_SECRET = getattr(secrets, "SOCIAL_AUTH_TWITTER_SECRET", "")
ENJAZACCOUNTS_TWITTER_KEY = getattr(secrets, "ENJAZACCOUNTS_TWITTER_KEY", "")
ENJAZACCOUNTS_TWITTER_SECRET = getattr(secrets, "ENJAZACCOUNTS_TWITTER_SECRET", "")
BITLY_KEY = getattr(secrets, "BITLY_KEY", None)

# Only set WKHTMLTOPDF_CMD if it isn't there.
if getattr(secrets, "WKHTMLTOPDF_CMD", False):
    WKHTMLTOPDF_CMD =  getattr(secrets, "WKHTMLTOPDF_CMD")

# Security settings
CORS_ORIGIN_ALLOW_ALL = True
SESSION_COOKIE_DOMAIN = getattr(secrets, "SESSION_COOKIE_DOMAIN", None)
CSRF_COOKIE_DOMAIN = getattr(secrets, "CSRF_COOKIE_DOMAIN", None)
SECURE_HSTS_SECONDS = getattr(secrets, "SECURE_HSTS_SECONDS", None)
