"""
Django settings for freesage project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)

PROJECT_ROOT = os.path.dirname(__file__)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'viu53jj296c1n)@^+!otd^lm!n&af20m5w$_oxe*(1k*alt424'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', True)
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.warning_exception_middleware.ProcessExceptionMiddleware',
)

print "MIDDLEWARE GOOD"

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'freesage.wsgi.application'

print "WSGI GOOD"

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('MVP_DB_NAME', 'freesage_db'),
        'USER': os.environ.get('POSTGRES_DB_USER', 'fuiste'),
        'PASSWORD': os.environ.get('POSTGRES_DB_PASS', ''),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

print "DATABASES GOOD"

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = "staticfiles"

if DEBUG:
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static/static_serve/')
    print STATIC_ROOT

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

APPEND_SLASH = False

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
)

INTERNAL_APPS = [
    'app'
]

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'tastypie',
]

print "APPS GOOD"

INSTALLED_APPS = INTERNAL_APPS + EXTERNAL_APPS

import dj_database_url

db_config =  dj_database_url.config()
if db_config:
    DATABASES["default"] = db_config

print "DJ_DATABASE_GOOD"
