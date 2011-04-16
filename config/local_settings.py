# -*- coding: utf-8 -*-

LOCAL_DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

#staticfiles

STATIC_ROOT = "/home/%(user)s/static"
STATIC_URL = "/media/"

MEDIA_ROOT = '%%s/media' %% STATIC_ROOT
MEDIA_URL = '%%s/media/' %% STATIC_URL

#django-contact-form
DEFAULT_FROM_EMAIL = 'contactform@foo'

MANAGERS = (
    ('fooper','fooper@foo'),
)

ADMIN_MEDIA_PREFIX = '%%sadmin/' %% STATIC_URL
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%(db_name)s',                      # Or path to database file if using sqlite3.
        'USER': '%(db_user)s',                      # Not used with sqlite3.
        'PASSWORD': '%(db_password)s',                  # Not used with sqlite3.
        'HOST': '%(db_host)s',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ABC'
EMAIL_HOST_PASSWORD = 'ABC'
EMAIL_USE_TLS = True

CACHE_BACKEND = 'locmem:///'
CACHE_MIDDLEWARE_SECONDS = 60*5
CACHE_MIDDLEWARE_KEY_PREFIX = '%(project_name)s.'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

INTERNAL_IPS = ('127.0.0.1',)

%(extra_settings)s
