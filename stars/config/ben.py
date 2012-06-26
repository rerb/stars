"""
    Personal config file for development in Ben's local environment.
"""


from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/Users/jamstooks/tmp/stars-email-messages'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# no emails during local dev
ADMINS = ('ben@aashe.org',)
MANAGERS = ADMINS

DATABASES = {
    'default': {
#         'NAME': '/Users/jamstooks/sqlite/pre1.2_test.db',
#         'ENGINE': 'sqlite3',
        'NAME': 'stars_ben',
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

MEDIA_ROOT = '/Users/jamstooks/workspace/media/stars/'

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

# Authorize.Net
#AUTHORIZENET_LOGIN = REAL_AUTHORIZENET_LOGIN
#AUTHORIZENET_KEY = REAL_AUTHORIZENET_KEY
#AUTHORIZENET_SERVER = REAL_AUTHORIZENET_SERVER

#CACHE_BACKEND = "file:///Users/jamstooks/tmp/stars-cache"
#CACHE_BACKEND = "dummy://"
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'temp_cache_table',
#        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#        'LOCATION': '/Users/jamstooks/tmp/stars-cache',
    }
}

# Authorize.Net
AUTHORIZENET_LOGIN = TEST_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = TEST_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = TEST_AUTHORIZENET_SERVER

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp/stars-cache',
        }
    }
    DATABASES['default']['ENGINE'] = 'sqlite3'
    DATABASES['default']['NAME'] = '/Users/jamstooks/sqlite/stars_tests.db'
    DATABASES['default']['OPTIONS'] = {}
    
# Thumbnails
THUMBNAIL_DEBUG = True