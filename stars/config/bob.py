"""
    Personal config file for development in Bob's local environment.
"""
import os

# monkey patches for pudb:
import urwid.raw_display
urwid.raw_display.Screen.signal_init = lambda x : None
urwid.raw_display.Screen.signal_restore = lambda x : None

from settings import *

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')

HIDE_REPORTING_TOOL = False
DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True

ADMINS = (('Bob Erb', 'bob@aashe.org'),)
MANAGERS = ADMINS

# Send emails to to django.core.mail.outbox rather than the console:
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

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

if ((('test' in sys.argv) or ('testserver' in sys.argv)) and
    use_sqlite_for_tests()):
    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('STARS_SQLITE_DB_URL'))
    DATABASES['iss'] = dj_database_url.parse(
        os.environ.get('ISS_SQLITE_DB_URL'))
else:
    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('STARS_MYSQL_DB_URL'))
    DATABASES['iss'] = dj_database_url.parse(
        os.environ.get('ISS_MYSQL_DB_URL'))

DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

INSTALLED_APPS += ('django_extensions',
                   'django_nose',
                   'template_repl')

if 'TEST_RUNNER' in os.environ:  # django_nose.NoseTestSuiteRunner, for example
    if os.environ['TEST_RUNNER']:  # only use it if there's a value set
        TEST_RUNNER = os.environ['TEST_RUNNER'] or TEST_RUNNER

# Stuff copied from ben.py that I don't know what it is:

SSO_API_KEY = "8dca728d46c85b3fda4529692a7f7725"
SSO_SERVER_URI = "http://www.aashe.org/services/xmlrpc"
STARS_DOMAIN = "localhost"
SSO_API_KEY = "e4c8dcfbcb5120ad35b516b04cc35302"

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True


# Thumbnails
THUMBNAIL_DEBUG = True

# django toolbar
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES.append(
        'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

TEMPLATE_STRING_IF_INVALID = 'INVALID EXPRESSION: %s' if DEBUG else ' '

# TEST_RUNNER = 'hotrunner.HotRunner'
# EXCLUDED_TEST_APPS = ['aashe.issdjango',
#                       'south',
#                       'sorl.thumbnail',
#                       'captcha',
#                       'django_extensions',
#                       'djcelery',
#                       'logical_rules',
#                       'tastypie',
#                       'bootstrapform',
#                       'memcache_status',
#                       's3_folder_storage',
#                       'stars.apps',
#                       'django_extensions',
#                       'django_nose',
#                       'template_repl']
