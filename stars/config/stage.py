"""
    This file configures the staging environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'stars_stage'
DATABASE_USER = 'starsapp'
DATABASE_PASSWORD = 'J3z4#$szFET--6'
DATABASE_HOST = 'localhost'

MEDIA_ROOT = '/var/www/vhosts/stage.aashe.org/subdomains/httpdocs/stars/media/'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
