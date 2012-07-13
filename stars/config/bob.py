"""
    Personal config file for development in Bob's local environment.
"""

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True

ADMINS = ('bob.erb@aashe.org',)
MANAGERS = ADMINS

if 'test' not in sys.argv:
    API_TEST_MODE = True
else:
    API_TEST_MODE = False

if (('test' not in sys.argv) and
    ('testserver' not in sys.argv)):
    DATABASES = {
        'default': {
            'NAME': 'stars',
            'ENGINE': 'django.db.backends.mysql',
            'STORAGE_ENGINE': 'MyISAM',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'OPTIONS': {
                "connect_timeout": 30,
                },
                },
        'iss': {
            'NAME': 'iss',
            'ENGINE': 'django.db.backends.mysql',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            }
    }

else:
    DATABASES = {
        'default': {
            'NAME': '/Users/rerb/sqlite/stars.db',
            'ENGINE': 'django.db.backends.sqlite3',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            },
        'iss': {
            'NAME': '/Users/rerb/sqlite/iss.db',
            'ENGINE': 'django.db.backends.sqlite3',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            }
    }

DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

INSTALLED_APPS += ('django_nose',
                   'fixture_magic')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
