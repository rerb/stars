"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'stars',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '33.33.33.20',
    },
    'iss': {
        'NAME': 'iss',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '33.33.33.20',
    }
}
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"

MEDIA_ROOT = '/var/www/stars.dev.aashe.org/media/'

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