"""
Personal config file for development in Jesse's local environment.
"""

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TESTING=True

# no emails during local dev
ADMINS = ('jesse.legg@aashe.org',)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'stars_jesse',
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

INSTALLED_APPS = INSTALLED_APPS + ('aashe.issdjango',)
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

MEDIA_ROOT = '/Users/jesse/src/stars/media/'


#AASHE_MYSQL_SERVER = "67.192.170.227"#"mysql.aashe.net" #"174.143.240.117"
AASHE_MYSQL_SERVER = "localhost"
AASHE_MYSQL_LOGIN = "root"
AASHE_MYSQL_PASS = ""

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

#CYBERSOURCE_URL = CYBERSOURCE_TEST_URL

# #if manage.py test was called, use test settings
# if 'test' in sys.argv:
#     DATABASES['default']['ENGINE'] = 'sqlite3'
#     DATABASES['default']['NAME'] = '/Users/jesse/src/stars_tests.db'

SOUTH_TESTS_MIGRATE=False

# Stuff copied from ben.py that I don't know what it is:

SSO_API_KEY = "8dca728d46c85b3fda4529692a7f7725"
SSO_SERVER_URI = "http://www.aashe.org/services/xmlrpc"
STARS_DOMAIN = "localhost"
SSO_API_KEY = "e4c8dcfbcb5120ad35b516b04cc35302"

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# Thumbnails
THUMBNAIL_DEBUG = True

AASHE_DRUPAL_URI = os.environ.get('AASHE_DRUPAL_URI', None)
AASHE_DRUPAL_KEY = os.environ.get('AASHE_DRUPAL_KEY', None)
AASHE_DRUPAL_KEY_DOMAIN = os.environ.get('AASHE_DRUPAL_KEY_DOMAIN', None)
AASHE_DRUPAL_COOKIE_SESSION = os.environ.get('AASHE_DRUPAL_COOKIE_SESSION', None)
AASHE_DRUPAL_COOKIE_DOMAIN = os.environ.get('AASHE_DRUPAL_COOKIE_DOMAIN', None)
AASHE_AUTH_VERBOSE = True
