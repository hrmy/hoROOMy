from .base import *

# Basic

DEBUG = True
ALLOWED_HOSTS = ['*']

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Console email backend

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'