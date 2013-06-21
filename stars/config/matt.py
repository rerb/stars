"""
    Personal config file for development in Matt's local environment.
"""
import os

from settings import *

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = DEBUG
MAINTENANCE_MODE = False
CELERY_ALWAYS_EAGER = True
PROFILE = False

ADMINS = (('Matt', 'mthomas@aashe.org'),)
MANAGERS = ADMINS

# Send emails to to django.core.mail.outbox rather than the console:
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Stuff copied from ben.py that I don't know what it is:

SSO_API_KEY = "8dca728d46c85b3fda4529692a7f7725"
SSO_SERVER_URI = "http://www.aashe.org/services/xmlrpc"
STARS_DOMAIN = "localhost"
SSO_API_KEY = "e4c8dcfbcb5120ad35b516b04cc35302"

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# Thumbnails
THUMBNAIL_DEBUG = True

AASHE_DRUPAL_URI = os.environ.get('AASHE_DRUPAL_URI', None)
AASHE_DRUPAL_KEY = os.environ.get('AASHE_DRUPAL_KEY', None)
AASHE_DRUPAL_KEY_DOMAIN = os.environ.get('AASHE_DRUPAL_KEY_DOMAIN', None)
AASHE_DRUPAL_COOKIE_SESSION = os.environ.get('AASHE_DRUPAL_COOKIE_SESSION', None)
AASHE_DRUPAL_COOKIE_DOMAIN = os.environ.get('AASHE_DRUPAL_COOKIE_DOMAIN', None)
AASHE_AUTH_VERBOSE = True
