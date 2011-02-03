"""
    This file configures the staging environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

MAINTENANCE_MODE = False

DATABASES = {
    'default': {
        'NAME': 'stars_stage',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '10.176.130.236',
    }
}

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

ANALYTICS_ID = "UA-1056760-7"

MEDIA_ROOT = '/var/www/stars.stage.aashe.org/media/'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY
