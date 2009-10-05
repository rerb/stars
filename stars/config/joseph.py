from settings import *

# no emails during local dev
ADMINS = ()
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/Users/Joseph/Misc/sqlite/stars.db'

# Add the default auth backend so that automated test suite runs correctly.
TESTING = True
if TESTING:
    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + ('django.contrib.auth.backends.ModelBackend',)
if not TESTING:  # dummy cache won't work for django.contrib.sessions tests, which rely on cache being available.
    CACHE_BACKEND = "dummy://" 

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True
DEBUG = True

MEDIA_ROOT = '/Users/Joseph/Projects/AASHE/STARS/media/'

#STARS_DOMAIN = DEV_STARS_DOMAIN
#SSO_API_KEY = DEV_SSO_API_KEY

SSO_SERVER_URI = WWW_SSO_SERVER_URI

#AASHE_MYSQL_SERVER = "mysql.aashe.org"
AASHE_MYSQL_SERVER = "67.192.170.227"

# XML RPC
XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True
