"""
@author: Thomas PERROT

Contains celery settings for mtg project
"""


from __future__ import absolute_import, unicode_literals
import os

from celery import Celery, shared_task
from celery.utils.log import get_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
app = Celery('mtg')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

logger = get_task_logger(__name__)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@shared_task(name='dummy')
def dummy():
    logger.critical('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
