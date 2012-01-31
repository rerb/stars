"""
    This file configures the production environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

MAINTENANCE_MODE = False

DATABASES = {
    'default': {
        'NAME': 'stars_production',
        'ENGINE': 'django.db.backends.mysql',
        'STORAGE_ENGINE': 'MyISAM',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'mysql.aashe.net',
    },
    'iss': {
        'NAME': 'iss',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'mysql.aashe.net',
    }
}
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
# GraphicsMagick is installed on the production server

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

ANALYTICS_ID = "UA-1056760-7"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

MEDIA_ROOT = '/var/www/stars.aashe.org/media/'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

# Authorize.Net
AUTHORIZENET_LOGIN = REAL_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = REAL_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = REAL_AUTHORIZENET_SERVER