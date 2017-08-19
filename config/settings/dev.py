from .base import *

# SECURTY CONFIGURATION

DEBUG = env.bool('DJANGO_DEBUG', True)
ALLOWED_HOSTS = ['*']

# CELERY CONFIGURATION

INSTALLED_APPS += ('kombu.transport.django',)
BROKER_URL = 'django://'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
