"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

# MAINTENANCE_MODE = True
# BROADCAST_MESSAGE = "The site is down for some temporary maintenance. We hope to be back up by 8pm."

from settings import *

DEBUG = False

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'stars_beta'
DATABASE_USER = 'starsapp'
DATABASE_PASSWORD = 'J3z4#$szFET--6'
DATABASE_HOST = 'localhost'

MEDIA_ROOT = '/var/www/stars.beta.aashe.org/media'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = DEV_STARS_DOMAIN
SSO_API_KEY = DEV_SSO_API_KEY

XMLRPC_VERBOSE = False

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL

ANALYTICS_ID = "UA-1056760-8"