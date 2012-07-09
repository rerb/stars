"""
    Personal config file for development in Bob's local environment.
"""

from bob import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True

ADMINS = ('bob.erb@aashe.org',)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': '/Users/rerb/sqlite/stars.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
    },
    'iss': {
        'NAME': '/Users/rerb/sqlite/iss.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

API_TEST_MODE = False

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

# django toolbar
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

# INSTALLED_APPS += ('django_nose',)

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
