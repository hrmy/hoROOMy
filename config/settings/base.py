import environ
env = environ.Env()

# PATH CONFIGURATION

ROOT_DIR = environ.Path(__file__) - 3  # (horoomy/config/settings/base.py - 3 = horoomy/)
APPS_DIR = ROOT_DIR.path('horoomy')

# SECUTIRY CONFIGURATION

ADMIN_URL = r'^admin/'
SECRET_KEY = 'qz^8j%)14z6o(spc+&#qq*ec888=rnjc^^$p-v6!w(vq!rwvkq'

# GENERAL CONFIGURATION

SITE_ID = 1
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# APP CONFIGURATION

DJANGO_APPS = [
    # Default
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Admin
    'django.contrib.admin',
]

THIRD_PARTY_APPS = [
    # AllAuth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.vk',
    
    # Utils
    'phonenumber_field',
    'djcelery',
    'annoying',
    'easy_pdf',
]

LOCAL_APPS = [
    'horoomy.accounts',
    'horoomy.core',
    'horoomy.parsers',
    'horoomy.docs',
    'horoomy.proxy',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# MIGRATIONS CONFIGURATION (???)

# MIGRATION_MODULES = {
#     'sites': 'horoomy.contrib.sites.migrations'
# }

# FIXTURE CONFIGURATION

FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION

EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'horoomy2017@gmail.com'
EMAIL_HOST_PASSWORD = 'moscowestate'
DEFAULT_EMAIL_FROM = 'horoomy2017@gmail.com'
EMAIL_USE_TLS = True

TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django.TemplateBackend'
TEMPLATED_EMAIL_AUTO_PLAIN = False

# MANAGER CONFIGURATION (???)

# ADMINS = [
#     ('AndBondStyle', 'AndBondStyle@gmail.com'),
# ]

# MANAGERS = ADMINS

# DATABASE CONFIGURATION

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://localhost/horoomy'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

# TEMPLATE CONFIGURATION

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# STATIC FILES CONFIGURATION

STATIC_URL = '/static/'
STATIC_ROOT = str(ROOT_DIR.path('staticfiles'))

STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION (???)

# MEDIA_ROOT = str(APPS_DIR('media'))
# MEDIA_URL = '/media/'

# URL CONFIGURATION

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# PASSWORDS CONFIGURATION

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# AUTHENTICATION CONFIGURATION

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'accounts.User'
ACCOUNT_ADAPTER = 'accounts.adapter.UserAccountAdapter'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'name'
ACCOUNT_USERNAME_REQUIRED = False

SOCIALACCOUNT_ADAPTER = 'accounts.adapter.UserSocialAccountAdapter'
SOCIALACCOUNT_PROVIDERS =  {
    'vk': {
        'SCOPE': ['email'],
    }, 
    'google': {
        'SCOPE': ['email'],
    }
}

# LOGIN CONFIGURATION

# LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
