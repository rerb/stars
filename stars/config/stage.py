"""
    This file configures the staging environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

MAINTENANCE_MODE = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'NAME': 'stars_stage',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'aashedb',
    },
    'iss': {
        'NAME': 'iss',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'aashedb',
    }
}
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

ANALYTICS_ID = "UA-1056760-7"

MEDIA_ROOT = '/var/www/stars.stage.aashe.org/media/'

SSO_SERVER_URI = STAGE_SSO_SERVER_URI
STARS_DOMAIN = STAGE_STARS_DOMAIN
SSO_API_KEY = STAGE_SSO_API_KEY
