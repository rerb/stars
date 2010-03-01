"""
    Personal config file for development in Ben's local environment.
"""

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# no emails during local dev
ADMINS = ('ben@aashe.org',)
MANAGERS = ADMINS

# DATABASE_ENGINE = 'sqlite3'
# DATABASE_NAME = '/Users/jamstooks/sqlite/stars.db'
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'stars_stage'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''
DATABASE_HOST = 'localhost'

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

MEDIA_ROOT = '/Users/jamstooks/aashe/STARS/src/media/stars/'

IRC_DOMAIN = WWW_IRC_DOMAIN

SSO_SERVER_URI = STAGE_SSO_SERVER_URI
STARS_DOMAIN = STAGE_STARS_DOMAIN
SSO_API_KEY = STAGE_SSO_API_KEY

#AASHE_MYSQL_SERVER = "67.192.170.227"#"mysql.aashe.net" #"174.143.240.117"
AASHE_MYSQL_SERVER = "localhost"
AASHE_MYSQL_LOGIN = "root"
AASHE_MYSQL_PASS = ""

XMLRPC_VERBOSE = True
XMLRPC_USE_HASH = True

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL
