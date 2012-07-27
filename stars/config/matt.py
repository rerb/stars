"""
    Personal config file for development in Matt's local environment.
"""

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TESTING=True

# no emails during local dev
ADMINS = ('mthomas@aashe.org',)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'stars_matt',
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

MEDIA_ROOT = '/Users/kuranes/aashe/stars/media/'

# XML RPC
XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# STARS_DOMAIN is used as part of hash key for securing rpc request.
WWW_STARS_DOMAIN = "stars.aashe.org"
STARS_DOMAIN = WWW_STARS_DOMAIN

# SSO_API_KEY is used to authenticate RPC requests
WWW_SSO_API_KEY = "8dca728d46c85b3fda4529692a7f7725"
SSO_API_KEY = WWW_SSO_API_KEY

WWW_SSO_SERVER_URI = "http://new.aashe.org/"

#AASHE_MYSQL_SERVER = "67.192.170.227"#"mysql.aashe.net" #"174.143.240.117"
AASHE_MYSQL_SERVER = "localhost"
AASHE_MYSQL_LOGIN = "root"
AASHE_MYSQL_PASS = ""

# Authorize.Net
AUTHORIZENET_LOGIN = TEST_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = TEST_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = TEST_AUTHORIZENET_SERVER
# #if manage.py test was called, use test settings
# if 'test' in sys.argv:
#     DATABASES['default']['ENGINE'] = 'sqlite3'
#     DATABASES['default']['NAME'] = '/Users/jesse/src/stars_tests.db'

SOUTH_TESTS_MIGRATE=False
