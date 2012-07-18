"""
    Personal config file for development in Bob's local environment.
"""
import os

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True

ADMINS = ('bob.erb@aashe.org',)
MANAGERS = ADMINS

def get_api_test_mode():
    try:
        return int(os.environ['API_TEST_MODE'])
    except KeyError:
        if 'test' in sys.argv:
            return False  # Unintuitive, isn't it? Should rename to AUTH_ON.
        else:
            return True  # If True, auth is turned off

API_TEST_MODE = get_api_test_mode()

def use_sqlite_for_tests():
    """If environmental variable USE_SQLITE_FOR_TESTS is not set or 1,
    use sqlite.  If it's 0, don't."""
    try:
        use_sqlite = os.environ['USE_SQLITE_FOR_TESTS']
    except KeyError:
        return True
    if use_sqlite:
        try:
            return bool(int(use_sqlite))
        except ValueError:
            raise Exception(
                "env var USE_SQLITE_FOR_TESTS should be int, not '{0}'".format(
                    use_sqlite))
    return True  # default

if (('test' in sys.argv) or ('testserver' in sys.argv)):
    if use_sqlite_for_tests():
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
    else:
        DATABASES = {
            'default': {
                'NAME': 'stars-test',
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
                'NAME': 'iss-test',
                'ENGINE': 'django.db.backends.mysql',
                'USER': 'root',
                'PASSWORD': '',
                'HOST': 'localhost',
                }
        }

else:
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


DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

INSTALLED_APPS += ('django_nose',
                   'fixture_magic')


if 'TEST_RUNNER' in os.environ: # django_nose.NoseTestSuiteRunner, for example
    if os.environ['TEST_RUNNER']:  # only use it if there's a value set
        TEST_RUNNER = os.environ['TEST_RUNNER'] or TEST_RUNNER
