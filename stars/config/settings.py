# Default Settings for STARS project
# These can be extended by any .py file in the config folder
import logging
import os
import re
import sys

import django
import django_cache_url
import dj_database_url
from celerybeat_schedule import STARS_TASK_SCHEDULE
from django.contrib.messages import constants as messages

sys.path.append('../')

ADMINS = (('Bob Erb', 'bob.erb@aashe.org'),
          ('Tylor Dodge', 'tylor@aashe.org'),
          ('Chris Pelton', 'chris.pelton@aashe.org'))
MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

DEBUG = os.environ.get("DEBUG", False)
TEMPLATE_DEBUG = DEBUG
API_TEST_MODE = os.environ.get("API_TEST_MODE", DEBUG)
FIXTURE_DIRS = ('fixtures', os.path.join(PROJECT_PATH, 'apps/api/fixtures'),)
PROFILE = os.environ.get("PROFILE", False)

USE_TZ = True
TIME_ZONE = 'America/Lima'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = False

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('STARS_DB_URL', None))
}

DATABASES['default']['OPTIONS'] = {'init_command':
                                   'SET default_storage_engine=MYISAM'}

# Media
USE_S3 = os.environ.get('USE_S3', None)

if USE_S3:
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    DEFAULT_S3_PATH = "media"
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
    STATIC_S3_PATH = "static"
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', None)

    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = 'https://s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = 'https://s3.amazonaws.com/%s/static/' % (
        AWS_STORAGE_BUCKET_NAME)
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

else:
    MEDIA_URL = '/media/'
    STATIC_URL = "/media/static/"
    MEDIA_ROOT = os.environ.get("MEDIA_ROOT", None)
    STATIC_ROOT = os.environ.get("STATIC_ROOT", '')

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), "..", "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

SECRET_KEY = 'omxxweql@m7!@yh5a-)=f^_xo*(m2+gaz#+8dje)e6wv@q$v%@'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

if not DEBUG:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader',
         TEMPLATE_LOADERS),
    )

LANGUAGES = [
    ('en', 'English'),
]

CMS_TEMPLATES = (
    ('cms/article_detail.html', 'Article Detail'),
)

MIDDLEWARE_CLASSES = [  # a list so it can be editable during tests (see below)
    ('raven.contrib.django.raven_compat.middleware.'
     'SentryResponseErrorIdMiddleware'),
    'stars.apps.helpers.utils.StripCookieMiddleware',
    'django_password_protect.PasswordProtectMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware']

CACHES = {
    'default': django_cache_url.parse(
        os.environ.get('CACHE_URL', 'dummy://')),
    'filecache': django_cache_url.parse(
        os.environ.get('FILE_CACHE_URL', 'file:///tmp/filecache'))
}

AUTHENTICATION_BACKENDS = (
    'django_membersuite_auth.backends.MemberSuiteBackend',)
if 'test' in sys.argv:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_membersuite_auth.backends.MemberSuiteBackend')

DASHBOARD_URL = "/tool/"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
LOGIN_REDIRECT_URL = "/"
ADMIN_URL = "/tool/admin/"
MANAGE_INSTITUTION_URL = "/tool/"
MANAGE_USERS_URL = MANAGE_INSTITUTION_URL + "manage/users/"

ROOT_URLCONF = 'stars.urls'

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), "..", "templates")]

# Use a custom context processor to get all the account and user info
# to the templates
TEMPLATE_CONTEXT_PROCESSORS = (
    "stars.apps.accounts.utils.account_context",
    'stars.apps.helpers.utils.settings_context',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    "django.contrib.auth.context_processors.auth",
    'django.core.context_processors.request',
    'django_settings_export.settings_export'
)

INSTALLED_APPS = (
    'longerusernameandemail',  # might need to be first

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.redirects',
    'django.contrib.flatpages',
    'django.contrib.formtools',
    'django.contrib.humanize',
    'django.contrib.staticfiles',

    'terms',  # must come before stars.apps.tool, which overrides the admin

    'stars.apps.credits',
    'stars.apps.tool.credit_editor',
    'stars.apps.tool.my_submission',
    'stars.apps.tool.staff_tool',
    'stars.apps.tool.manage',
    'stars.apps.tool',
    'stars.apps.institutions',
    "stars.apps.institutions.data_displays",
    'stars.apps.registration',
    'stars.apps.submissions',
    'stars.apps.accounts',
    'stars.apps.helpers',
    'stars.apps.helpers.forms',  # included here for testing
    'stars.apps.old_cms',
    'stars.apps.custom_forms',
    'stars.apps.tasks',
    'stars.apps.notifications',
    'stars.apps.migrations',
    'stars.apps.third_parties',
    'stars.apps.api',
    'stars.apps.download_async_task',
    'stars.apps.bt_etl',
    # 'stars.tests',

    'adv_cache_tag',
    'bootstrapform',
    'captcha',
    'collapsing_menu',
    'compressor',
    'compressor',
    'django_celery_downloader',
    'django_celery_downloader.tests.demo_app',
    'django_extensions',
    'django_membersuite_auth',
    'djcelery',
    'file_cache_tag',
    'gunicorn',
    'iss',
    'logical_rules',
    'raven.contrib.django.raven_compat',
    's3_folder_storage',
    'sorl.thumbnail',
    'south',
    'tastypie',
    'localflavor',
)

if 'test' in sys.argv:
    INSTALLED_APPS += ('stars.test_factories',
                       'stars.apps.payments')

# Permissions or user levels for STARS users
STARS_PERMISSIONS = (
    ('admin', 'Administrator'),
    ('submit', 'Data Entry'),
    ('view', 'Observer'))

# Email
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.filebased.EmailBackend')
EMAIL_FILE_PATH = os.environ.get(
    'EMAIL_FILE_PATH', '/tmp/stars-email-messages')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)

EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', None)
EMAIL_REPLY_TO = os.environ.get('EMAIL_REPLY_TO', None)

# sorl thumbnail
# THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_FORMAT = 'PNG'
THUMBNAIL_DEBUG = os.environ.get("THUMBNAIL_DEBUG", False)

# Celery
# import djcelery
# djcelery.setup_loader()
CELERY_TIMEZONE = 'US/Eastern'
CELERYBEAT_SCHEDULE = STARS_TASK_SCHEDULE
BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672/')
CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER', False)
CELERY_RESULT_BACKEND = os.environ.get(
    'CELERY_RESULT_BACKEND',
    'djcelery.backends.database:DatabaseBackend')
CELERY_RESULT_DBURI = os.environ.get('CELERY_RESULT_DBURI',
                                     "sqlite:///tmp/stars-celery-results.db")
CELERY_CACHE_BACKEND = os.environ.get('CELERY_CACHE_BACKEND', 'dummy')

# default is test mode
AUTHORIZENET_LOGIN = os.environ.get('AUTHORIZENET_LOGIN', None)
AUTHORIZENET_KEY = os.environ.get('AUTHORIZENET_KEY', None)

ANALYTICS_ID = os.environ.get('ANALYTICS_ID', None)

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', None)
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', None)
RECAPTCHA_USE_SSL = True

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', None)

PYTHON_VERSION = None
m = re.match('[\d\.]+', sys.version)
if m:
    PYTHON_VERSION = m.group(0)

DJANGO_VERSION = django.get_version()
HG_REVISION = None

# Sentry Logging: getsentry.com
RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_CONFIG_DSN', None),
}

# django-terms
TERMS_REPLACE_FIRST_ONLY = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'root': {
        'level': 'WARNING',
        'handlers': ['sentry']
    },

    'formatters': {
        # For log messages from third-parties, to which we can't
        # add module_name:
        'simple_formatter': {
            'format': ('%(levelname)s %(asctime)s "%(message)s" '
                       'location=%(pathname)s:%(funcName)s:%(lineno)s')
        },
        # The simplest custom formatter; module_name is added by
        # stars.apps.helpers.logging_filters.ModuleNameFilter.
        'stars_formatter': {
            'format': ('%(levelname)s %(asctime)s "%(message)s" '
                       'location=%(module_name)s:%(funcName)s:%(lineno)s')
        },
        # In additon to module_name, username is used in this formatter
        # (added by stars.apps.helpers.logging_filters.UserNameFilter).
        'stars_user_formatter': {
            'format': ('%(levelname)s %(asctime)s "%(message)s" '
                       'location=%(module_name)s:%(funcName)s:%(lineno)s '
                       'user=%(username)s')
        },
        # In addition to module_name, elements from a request are
        # included in this format (request elements added by
        # stars.apps.helpers.logging_filters.RequestFilter).
        'stars_request_formatter': {
            'format': (
                '%(levelname)s %(asctime)s "%(message)s" '
                'location=%(module_name)s:%(funcName)s:%(lineno)s '
                'user=%(request_user)s '
                'path=%(request_path)s '
                'host=%(request_host)s '
                'referer=%(request_referer)s')
        }
    },

    'filters': {
        'module_name_filter': {
            '()': 'stars.apps.helpers.logging_filters.ModuleNameFilter'
        },
        'request_filter': {
            '()': 'stars.apps.helpers.logging_filters.RequestFilter'
        },
        'user_filter': {
            '()': 'stars.apps.helpers.logging_filters.UserFilter'
        }
    },

    'handlers': {
        'simple_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple_formatter',
            'stream': sys.stdout
        },
        'stars_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stars_formatter',
            'stream': sys.stdout
        },
        'stars_request_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stars_request_formatter',
            'stream': sys.stdout
        },
        'stars_user_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stars_user_formatter',
            'stream': sys.stdout
        },
        'mail_admins_handler': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'sentry': {
            'level': 'ERROR',
            'class': ('raven.contrib.django.raven_compat.handlers.'
                      'SentryHandler')
        }
    },

    'loggers': {
        # root logger, for third party log messages:
        '': {
            'handlers': ['simple_console_handler', 'sentry']
        },
        'django.request': {
            'handlers': ['sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        # logger with module_name added to log record:
        'stars': {
            'handlers': ['stars_console_handler', 'sentry'],
            'propagate': False,
            'filters': ['module_name_filter']
        },
        # logger with module_name and username added to log record:
        'stars.user': {
            'handlers': ['stars_user_console_handler',
                         'sentry'],
            'propagate': False,
            'filters': ['module_name_filter', 'user_filter']
        },
        # logger with module_name and request elements added to log record:
        'stars.request': {
            'handlers': ['stars_request_console_handler',
                         'sentry'],
            'propagate': False,
            'filters': ['module_name_filter', 'request_filter']
        },
        'qinspect': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', 'mail_admins_handler'],
            'propagate': False
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', 'mail_admins_handler'],
            'propagate': False
        }
    }
}

# Twitter settings

####
# For AASHEConference Account:
# OAUTH_TOKEN = '1022657755-JZf8ELufzotuIQLRcFud5Yma8AdLQoNIpfgIGAe'
# OAUTH_SECRET = 'KYa5e5KmSvueKKAaayKYWw7RNBBGz7EDcQxTEs5ggOw'
# CONSUMER_KEY = 'yUIhK70Fd4YGwBccC0QIfg'
# CONSUMER_SECRET = 'XDgsAa6AXoGM7TETZyijPRZtvqausyvTA4Gulg'

####
# For AASHENews Account:
OAUTH_TOKEN = '56789085-UeceFRK4gXmPORn8xSXEMl0huvTzvAu7V20vXxuVA'
OAUTH_SECRET = 'PuYN5kEDD5s1orK8Xk65v6pWZTzEzw1ny5vgiKU'
CONSUMER_KEY = 'clTv8jtn1Pq4oKtucPxmMg'
CONSUMER_SECRET = 's9aIjWEgy4EkbDgK14CkBlDwuAySykYZrtquQiTg'

if sys.version >= '2.7':
    logging.captureWarnings(True)

MESSAGE_TAGS = {
    messages.DEBUG: 'alert fade in alert-debug',
    messages.INFO: 'alert fade in alert-info',
    messages.SUCCESS: 'alert fade in alert-success',
    messages.WARNING: 'alert fade in alert-warning',
    messages.ERROR: 'alert fade in alert-error'}

if os.path.exists(os.path.join(os.path.dirname(__file__), 'hg_info.py')):
    from hg_info import revision
    HG_REVISION = revision

# django toolbar
DEBUG_TOOLBAR = os.environ.get('DEBUG_TOOLBAR', False)
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + [
        'debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

AUTHORIZE_CLIENT_TEST = os.environ.get('AUTHORIZE_CLIENT_TEST', False)
AUTHORIZE_CLIENT_DEBUG = os.environ.get('AUTHORIZE_CLIENT_DEBUG', False)

# Test backends
if 'test' in sys.argv:
    # until fix for http://code.djangoproject.com/ticket/14105
    MIDDLEWARE_CLASSES.remove(
        'django.middleware.cache.FetchFromCacheMiddleware')
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.UpdateCacheMiddleware')
    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('STARS_TEST_DB',
                       "sqlite:////tmp/stars_tests.db"))
    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('ISS_TEST_DB',
                       "sqlite:////tmp/iss_tests.db"))

    CACHES = {
        'default': django_cache_url.parse(
            os.environ.get('CACHE_URL_TEST', 'dummy://')),
        'filecache': django_cache_url.parse(
            os.environ.get('FILE_CACHE_URL_TEST', 'file:///tmp/filecache'))
    }

    API_TEST_MODE = False

    AUTHORIZENET_LOGIN = os.environ.get('AUTHORIZENET_TEST_LOGIN', None)
    AUTHORIZENET_KEY = os.environ.get('AUTHORIZENET_TEST_KEY', None)

    AUTHORIZE_CLIENT_TEST = True
    AUTHORIZE_CLIENT_DEBUG = True

# Override default of compression off when debug=true to test locally
COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED')

AUTH_USER_MODEL = 'auth.User'

# Performance
QUERY_INSPECT_ENABLED = os.environ.get('QUERY_INSPECT_ENABLED', False)
MIDDLEWARE_CLASSES += (
    'qinspect.middleware.QueryInspectMiddleware',
)

# optional password for dev sites
PASSWORD_PROTECT = os.environ.get('PASSWORD_PROTECT', False)
PASSWORD_PROTECT_USERNAME = os.environ.get('PASSWORD_PROTECT_USERNAME', None)
PASSWORD_PROTECT_PASSWORD = os.environ.get('PASSWORD_PROTECT_PASSWORD', None)
PASSWORD_PROTECT_REALM = os.environ.get(
    'PASSWORD_PROTECT_REALM', 'Dev Site Auth')

SOUTH_MIGRATION_MODULES = {
    'iss': 'iss.south_migrations',
}

############################
# Membersuite
############################
MS_ACCESS_KEY = os.environ["MS_ACCESS_KEY"]
MS_SECRET_KEY = os.environ["MS_SECRET_KEY"]
MS_ASSOCIATION_ID = os.environ["MS_ASSOCIATION_ID"]
STARS_MS_PUBLICATION_ID = os.environ["STARS_MS_PUBLICATION_ID"]

############################
# longerusernameandemail
############################
REQUIRE_UNIQUE_EMAIL = False

STARS_BROCHURE_HOST = os.environ["STARS_BROCHURE_HOST"]
STARS_REPORTS_HOST = os.environ["STARS_REPORTS_HOST"]
STARS_BENCHMARKS_HOST = os.environ["STARS_BENCHMARKS_HOST"]

SETTINGS_EXPORT = ["STARS_BROCHURE_HOST",
                   "STARS_REPORTS_HOST",
                   "STARS_BENCHMARKS_HOST"]
