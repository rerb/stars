"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'stars_dev',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '10.176.128.183',
    },
    'iss': {
        'NAME': 'iss',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '10.176.128.183',
    }
}
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
# CACHE_BACKEND = "dummy://"

THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
#CACHE_BACKEND = "db://temp_cache_table"

MEDIA_ROOT = '/var/www/stars.aashe.org/media/'

SSO_SERVER_URI = DEV_SSO_SERVER_URI
STARS_DOMAIN = DEV_STARS_DOMAIN
SSO_API_KEY = DEV_SSO_API_KEY

XMLRPC_VERBOSE = False

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    
    CACHE_BACKEND = "file:///tmp/stars-cache"
    # Authorize.Net
    AUTHORIZENET_LOGIN = REAL_AUTHORIZENET_LOGIN
    AUTHORIZENET_KEY = REAL_AUTHORIZENET_KEY
    AUTHORIZENET_SERVER = REAL_AUTHORIZENET_SERVER