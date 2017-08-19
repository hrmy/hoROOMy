from celery import Celery
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.pro")

app = Celery('horoomy')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
