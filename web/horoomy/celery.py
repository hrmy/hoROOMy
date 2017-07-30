from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

from datetime import timedelta


os.environ['DJANGO_SETTINGS_MODULE'] = 'horoomy.settings.dev'
django.setup()

app = Celery('horoomy')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


