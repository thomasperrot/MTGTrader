"""
@author: Thomas PERROT

Contains production settings for mtg project
"""


import logging

from .base import *


logging.basicConfig(level=logging.WARNING)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mtg',
        'USER': get_env_variable('DB_USER'),
        'PASSWORD': get_env_variable('DB_PASSWORD'),
        'HOST': 'postgres',
        'PORT': '',
    },
}

BROKER_URL = 'amqp://{user}:{password}@{hostname}//'.format(
    user=get_env_variable('RABBIT_USER'),
    password=get_env_variable('RABBIT_PASSWORD'),
    hostname=RABBIT_HOSTNAME
)

BROKER_API = 'http://{user}:{password}@{hostname}:15672/api/'.format(
    user=get_env_variable('RABBIT_USER'),
    password=get_env_variable('RABBIT_PASSWORD'),
    hostname=RABBIT_HOSTNAME
)
