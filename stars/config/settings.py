# Default Settings for STARS project
# These can be extended by any .py file in the config folder
import logging, os, sys, django, re
from django.contrib.messages import constants as messages

sys.path.append('../')

ADMINS = (('Benjamin Stookey', 'ben@aashe.org'),('Bob Erb', 'bob.erb@aashe.org'))
MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

DEBUG = os.environ.get("DEBUG", False)
TEMPLATE_DEBUG = DEBUG
API_TEST_MODE = os.environ.get("API_TEST_MODE", DEBUG)
FIXTURE_DIRS = ('fixtures', os.path.join(PROJECT_PATH, 'apps/api/fixtures'),)

TIME_ZONE = 'America/Lima'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('STARS_DB_URL', None)),
    'iss': dj_database_url.parse(os.environ.get('ISS_DB_URL', None))
}
DATABASES['default']['OPTIONS'] = {'init_command': 'SET storage_engine=MYISAM'}
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

# Media
MEDIA_URL = '/media/'
STATIC_URL = "/media/static/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", None)

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), "..", "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'omxxweql@m7!@yh5a-)=f^_xo*(m2+gaz#+8dje)e6wv@q$v%@'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = [ # a list so it can be editable during tests (see below)
    'stars.apps.helpers.utils.StripCookieMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'aashe.aasheauth.middleware.AASHEAccountMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware']

import django_cache_url
CACHES = {'default': django_cache_url.parse(os.environ.get('CACHE_URL', 'dummy://'))}

AUTH_PROFILE_MODULE = 'accounts.UserProfile'
AUTHENTICATION_BACKENDS = ('aashe.aasheauth.backends.AASHEBackend',)
if 'test' in sys.argv:
    AUTHENTICATION_BACKENDS = (
                               'django.contrib.auth.backends.ModelBackend',
                               'aashe.aasheauth.backends.AASHEBackend',
                               # 'stars.apps.accounts.aashe.AASHEAuthBackend',
                               )

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
    "django.contrib.auth.context_processors.auth")

INSTALLED_APPS = (
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
    'stars.apps.credits',
    'stars.apps.tool.credit_editor',
    'stars.apps.tool.my_submission',
    'stars.apps.tool.admin',
    'stars.apps.tool.manage',
    'stars.apps.institutions',
    "stars.apps.institutions.data_displays",
    'stars.apps.registration',
    'stars.apps.submissions',
    'stars.apps.accounts',
    'stars.apps.helpers',
    'stars.apps.helpers.forms', # included here for testing
    'stars.apps.cms',
    'stars.apps.etl_export',
    'stars.apps.custom_forms',
    'stars.apps.tasks',
    'stars.apps.notifications',
    'stars.apps.migrations',
    'stars.apps.third_parties',
    'stars.apps.api',
    'stars.tests',

    'logical_rules',
    'aashe.aasheauth',
    'aashe.issdjango',
    'bootstrapform',
    'captcha',
    'django_extensions',
    'djcelery',
    'sorl.thumbnail',
    'south',
    's3_folder_storage',
    'tastypie',
    'gunicorn',
)

# aasheauth config
AASHE_DRUPAL_URI = os.environ.get('AASHE_DRUPAL_URI', None)
AASHE_DRUPAL_KEY = os.environ.get('AASHE_DRUPAL_KEY', None)
AASHE_DRUPAL_KEY_DOMAIN = os.environ.get('AASHE_DRUPAL_KEY_DOMAIN', None)
AASHE_DRUPAL_COOKIE_SESSION = os.environ.get('AASHE_DRUPAL_COOKIE_SESSION', None)
AASHE_DRUPAL_COOKIE_DOMAIN = os.environ.get('AASHE_DRUPAL_COOKIE_DOMAIN', None)
AASHE_AUTH_VERBOSE = os.environ.get('AASHE_AUTH_VERBOSE', False)

# Permissions or user levels for STARS users
STARS_PERMISSIONS = (('admin', 'Administrator'), ('submit', 'Data Entry'), ('view', 'Observer')) # ('review', 'Audit/Review'))

# Email
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', None)
EMAIL_REPLY_TO = os.environ.get('EMAIL_REPLY_TO', None)
EMAIL_FILE_PATH = os.environ.get('EMAIL_REPLY_TO', '/tmp/stars-email-messages')

# sorl thumbnail
#THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_FORMAT = 'PNG'
THUMBNAIL_DEBUG = os.environ.get("THUMBNAIL_DEBUG", False)

# Celery
import djcelery
djcelery.setup_loader()
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"
CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER', False)

CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'database')
CELERY_RESULT_DBURI = os.environ.get('CELERY_RESULT_DBURI', "sqlite:///tmp/stars-celery-results.db")
CELERY_CACHE_BACKEND = os.environ.get('CELERY_CACHE_BACKEND', 'dummy')

# default is test mode
AUTHORIZENET_LOGIN = os.environ.get('AUTHORIZENET_LOGIN', None)
AUTHORIZENET_KEY = os.environ.get('AUTHORIZENET_KEY', None)
AUTHORIZENET_SERVER = os.environ.get('AUTHORIZENET_SERVER', None)

ANALYTICS_ID = os.environ.get('ANALYTICS_ID', None)

SKIP_SOUTH_TESTS=True

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

SOUTH_TESTS_MIGRATE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

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
        }
    },

    'loggers': {
        # root logger, for third party log messages:
        '': {
            'handlers':['simple_console_handler', 'mail_admins_handler']
        },
        # logger with module_name added to log record:
        'stars': {
            'handlers': ['stars_console_handler', 'mail_admins_handler'],
            'propagate': False,
            'filters': ['module_name_filter']
        },
        # logger with module_name and username added to log record:
        'stars.user': {
            'handlers': ['stars_user_console_handler',
                         'mail_admins_handler'],
            'propagate': False,
            'filters' : ['module_name_filter', 'user_filter']
        },
        # logger with module_name and request elements added to log record:
        'stars.request': {
            'handlers': ['stars_request_console_handler',
                         'mail_admins_handler'],
            'propagate': False,
            'filters': ['module_name_filter', 'request_filter']
        }
    }
}

if sys.version >= '2.7':
    logging.captureWarnings(True)

MESSAGE_TAGS = { messages.DEBUG: 'alert fade in alert-debug',
                 messages.INFO : 'alert fade in alert-info',
                 messages.SUCCESS : 'alert fade in alert-success',
                 messages.WARNING : 'alert fade in alert-warning',
                 messages.ERROR : 'alert fade in alert-error' }

if os.path.exists(os.path.join(os.path.dirname(__file__), 'hg_info.py')):
    from hg_info import revision
    HG_REVISION = revision

# django toolbar
DEBUG_TOOLBAR = os.environ.get('DEBUG_TOOLBAR', False)
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

# Test backends
if 'test' in sys.argv:
    # until fix for http://code.djangoproject.com/ticket/14105
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.FetchFromCacheMiddleware')
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.UpdateCacheMiddleware')

    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('STARS_TEST_DB',
                       "sqlite:////tmp/stars_tests.db"))
    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('ISS_TEST_DB',
                       "sqlite:////tmp/iss_tests.db"))

    CACHES = {'default': django_cache_url.parse(os.environ.get('CACHE_TEST_URL', 'file:///tmp/stars-cache'))}

    API_TEST_MODE = False

    AUTHORIZENET_LOGIN = os.environ.get('AUTHORIZENET_TEST_LOGIN', None)
    AUTHORIZENET_KEY = os.environ.get('AUTHORIZENET_TEST_KEY', None)
    AUTHORIZENET_SERVER = os.environ.get('AUTHORIZENET_TEST_SERVER', None)

