"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

# Celery
# CELERY_RESULT_DBURI = "sqlite:///var/www/stars/stars-celery-results.db"
# CELERY_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
# os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
# os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')

CACHES = {
    'default': {
        # 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # 'LOCATION': os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';'),
        # 'TIMEOUT': 500,
        # 'BINARY': True,
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
DEFAULT_S3_PATH = "media"
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
STATIC_S3_PATH = "static"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "None")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "None")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "None")

MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
STATIC_ROOT = "/%s/" % STATIC_S3_PATH
STATIC_URL = '//s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

ANALYTICS_ID = "UA-1056760-7"

#THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_FORMAT = 'PNG'

# INSTALLED_APPS = INSTALLED_APPS + ('memcache_status',)

XMLRPC_VERBOSE = False