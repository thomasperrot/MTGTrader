"""
@author: Thomas PERROT

Contains local settings for mtg project
"""


import logging

from .base import *

logging.basicConfig(level=logging.DEBUG)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mtg',
        'USER': 'mtg',
        'PASSWORD': 'mtgmtg',
        'HOST': 'postgres',
        'PORT': '',
    }
}

INSTALLED_APPS += [
    'corsheaders',
    # 'django_extensions'
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ('GET',)

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE

CELERY_RESULT_BACKEND = 'amqp://guest:guest@{hostname}//'.format(hostname=CELERY_RABBIT_HOSTNAME)
CELERY_BROKER_URL = 'amqp://guest:guest@{hostname}//'.format(hostname=CELERY_RABBIT_HOSTNAME)
CELERY_BROKER_API = 'http://guest:guest@{hostname}:15672/api/'.format(hostname=CELERY_RABBIT_HOSTNAME)
