"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DEBUG = False

DATABASES = {
    'default': {
        'NAME': 'stars_production',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '174.143.240.185',
    },
    'iss': {
        'NAME': 'iss',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': '174.143.240.185',
    }
}
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"

MEDIA_ROOT = '/var/www/stars/media/'

INSTALLED_APPS = INSTALLED_APPS + ('memcache_status',)

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

XMLRPC_VERBOSE = False

# Authorize.Net
AUTHORIZENET_LOGIN = REAL_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = REAL_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = REAL_AUTHORIZENET_SERVER

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    
    CACHE_BACKEND = "file:///tmp/stars-cache"