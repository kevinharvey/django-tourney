import os

from tourney.settings.base import *

WSGI_APPLICATION = 'tourney.wsgi.application'


SITE_NAME = get_environment_variable('SITE_NAME')


ALLOWED_HOSTS = [os.environ.get('SERVER_NAME')]


SECRET_KEY = get_environment_variable('DJANGO_SECRET_KEY')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = get_environment_variable('EMAIL_HOST')
EMAIL_PORT = get_environment_variable('EMAIL_PORT')
EMAIL_HOST_USER = get_environment_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_environment_variable('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = get_environment_variable('DEFAULT_FROM_EMAIL')
DEFAULT_ORGANIZER_EMAIL = get_environment_variable('DEFAULT_ORGANIZER_EMAIL')

STATIC_ROOT = get_environment_variable('STATIC_ROOT')
