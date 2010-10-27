"""
    This file configures the production environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DATABASES = {
    'default': {
        'NAME': 'stars_production',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'localhost',
    }
}

ANALYTICS_ID = "UA-1056760-7"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

MEDIA_ROOT = '/var/www/stars.aashe.org/media'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

CYBERSOURCE_URL = CYBERSOURCE_PRODUCTION_URL
