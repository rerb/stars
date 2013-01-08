"""
    Personal config file for development in Ben's local environment.
"""


from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
API_TEST_MODE = False
DEBUG_TOOLBAR = False
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/Users/jamstooks/tmp/stars-email-messages'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# no emails during local dev
ADMINS = ('ben@aashe.org',)
MANAGERS = ADMINS

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# django toolbar
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'temp_cache_table',
#        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#        'LOCATION': '/Users/jamstooks/tmp/stars-cache',
    }
}

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp/stars-cache',
        }
    }
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # DATABASES['default']['ENGINE'] = 'sqlite3'
    # DATABASES['default']['NAME'] = '/Users/jamstooks/sqlite/stars_tests.db'
    # DATABASES['default']['OPTIONS'] = {}
    DATABASES['default'] = dj_database_url.parse(os.environ.get('STARS_TEST_DB', None))
    
# Thumbnails
THUMBNAIL_DEBUG = False
