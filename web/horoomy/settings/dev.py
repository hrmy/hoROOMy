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


CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# django-templated-email
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django.TemplateBackend'
TEMPLATED_EMAIL_AUTO_PLAIN = False

# console backend
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


