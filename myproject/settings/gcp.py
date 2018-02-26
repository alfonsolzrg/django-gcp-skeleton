from .base import *

import os

DEBUG = bool(int(os.environ.setdefault("DEBUG", "0")))
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'my_database',
        'USER': os.environ.setdefault("MAIN_DB_USER", ""),
        'PASSWORD': os.environ.setdefault("MAIN_DB_PASS", ""),
        'HOST': os.environ.setdefault("MAIN_DB_HOST", ""),
        'PORT': os.environ.setdefault("MAIN_DB_PORT", ""),
        'CONN_MAX_AGE': 600,
    }
}

CDN = os.environ.setdefault("CDN", "")
STATIC_ROOT = os.path.join(BASE_DIR, 'assets', GIT_SHA)
STATICFILES_DIRS = ()
STATIC_URL = "%s/%s/" % (CDN, GIT_SHA)

RAVEN_CONFIG = {
    'dsn': os.environ.setdefault("RAVEN_SENTRY_URL", ""),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': GIT_SHA,
}

CELERY_BROKER_URL = 'redis://:{}@{}:{}/{}'.format(
    os.environ.setdefault("BROKER_MAIN_PASSWORD", ""),
    os.environ.setdefault("BROKER_MAIN_SERVICE_HOST", ""),
    os.environ.setdefault("BROKER_MAIN_SERVICE_PORT", ""),
    os.environ.setdefault("BROKER_CELERY_DATABASE", "")
)
