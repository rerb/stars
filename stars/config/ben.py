"""
    Personal config file for development in Ben's local environment.
"""


from settings import *

DEBUG_TOOLBAR = False
CELERY_ALWAYS_EAGER = True

# no emails during local dev
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/stars-email-messages'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = ('ben@aashe.org',)
MANAGERS = ADMINS

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

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

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'temp_cache_table',
#        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#        'LOCATION': '/Users/jamstooks/tmp/stars-cache',
#     }
# }

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp/stars-cache',
        }
    }
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['default']['NAME'] = '/Users/jamstooks/sqlite/stars_tests.db'
    DATABASES['default']['OPTIONS'] = {}
    
    DATABASES['iss']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['iss']['NAME'] = '/Users/jamstooks/sqlite/stars_iss_tests.db'
    DATABASES['iss']['OPTIONS'] = {}
    
    API_TEST_MODE = False
    
# Thumbnails
THUMBNAIL_DEBUG = False
