"""
Django settings for django_rss project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
WEBCLIENT_DIR = os.path.join(PROJECT_DIR, "webclient/track-tracker")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c46f@@!32_7%b)*^dqtp7fj!!k(-*alycugik0vdey)8^q+vp%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wsgi.feeds',
    'wsgi.locations',
    'rest_framework',
    'django_extensions',
    'corsheaders',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'django_rss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [WEBCLIENT_DIR],
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

WSGI_APPLICATION = 'django_rss.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
	'ENGINE':   'django.db.backends.mysql',
	'NAME':     'service2',
	'USER':     os.environ.get('OPENSHIFT_MYSQL_DB_USERNAME', ""),
	'PASSWORD': os.environ.get('OPENSHIFT_MYSQL_DB_PASSWORD', ""),
	'HOST':     os.environ.get('OPENSHIFT_MYSQL_DB_HOST', ""),
	'PORT':     os.environ.get('OPENSHIFT_MYSQL_DB_PORT', ""),
    }
}

STATICFILES_DIRS = [
    os.path.join(WEBCLIENT_DIR, "static")
]


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

CORS_ORIGIN_ALLOW_ALL = True

MAP = os.path.join(os.environ.get("OPENSHIFT_DATA_DIR", STATIC_ROOT), 'map2.json')
MAP_ = os.path.join(os.environ.get("OPENSHIFT_DATA_DIR", STATIC_ROOT), 'map.json')
# MAP2 = os.path.join(STATIC_ROOT, 'map2.json')
GOOGLE_API_KEY = "AIzaSyBir6gtAnK2Ck9Te9ibcTbnO9SQKdQPBNg"

try:
    from .local_settings import *
except:
    pass
