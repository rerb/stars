"""
    Personal config file for development in Ben's local environment.
"""

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
MAINTENANCE_MODE = False

#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '~/tmp/stars-email-messages' # change this to a proper location

# no emails during local dev
ADMINS = ('ben@aashe.org',)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        # 'NAME': '/Users/jamstooks/sqlite/stars_test.db',
        # 'ENGINE': 'sqlite3',
        'NAME': 'stars_ben',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
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

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'sqlite3'
    DATABASES['default']['NAME'] = '/Users/jamstooks/sqlite/stars_tests.db'

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

MEDIA_ROOT = '/Users/jamstooks/aashe/projects/STARS/src/media/stars/'

SSO_SERVER_URI = STAGE_SSO_SERVER_URI
STARS_DOMAIN = STAGE_STARS_DOMAIN
SSO_API_KEY = STAGE_SSO_API_KEY

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# Authorize.Net
#AUTHORIZENET_LOGIN = REAL_AUTHORIZENET_LOGIN
#AUTHORIZENET_KEY = REAL_AUTHORIZENET_KEY
#AUTHORIZENET_SERVER = REAL_AUTHORIZENET_SERVER

#CACHE_BACKEND = "file:///Users/jamstooks/tmp/stars-cache"
CACHE_BACKEND = "dummy://"
#CACHE_BACKEND = "db://temp_cache_table"

# Authorize.Net
AUTHORIZENET_LOGIN = TEST_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = TEST_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = TEST_AUTHORIZENET_SERVER