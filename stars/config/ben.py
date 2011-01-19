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
        'NAME': 'stars_migrate',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
    },
#    'iss': {
#        'NAME': 'iss',
#        'ENGINE': 'django.db.backends.mysql',
#        'USER': 'root',
#        'PASSWORD': '',
#        'HOST': 'localhost',
#    }
}

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

MEDIA_ROOT = '/Users/jamstooks/aashe/projects/STARS/src/media/stars/'

IRC_DOMAIN = DEV_IRC_DOMAIN

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL

#CACHE_BACKEND = "file:///Users/jamstooks/tmp/stars-cache"
CACHE_BACKEND = "dummy://"
#CACHE_BACKEND = "db://temp_cache_table"

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'sqlite3'
    DATABASES['default']['NAME'] = '/Users/jamstooks/sqlite/stars_tests.db'

SOUTH_TESTS_MIGRATE = False

AASHE_MYSQL_SERVER = "localhost"
AASHE_MYSQL_LOGIN = "root"
AASHE_MYSQL_PASS = ""

URL_VALIDATOR_USER_AGENT = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.231 Safari/534.10"