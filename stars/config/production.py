"""
    This file configures the production environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

HIDE_REPORTING_TOOL = False

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'stars_production'
DATABASE_USER = 'starsapp'
DATABASE_PASSWORD = 'J3z4#$szFET--6'
DATABASE_HOST = 'localhost'

MEDIA_ROOT = '/var/www/stars.aashe.org/media'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

XMLRPC_VERBOSE = False

CYBERSOURCE_URL = CYBERSOURCE_PRODUCTION_URL
