# Default Settings for STARS project
# These can be extended by any .py file in the config folder
import logging, os, sys, django, re
from django.contrib.messages import constants as messages

sys.path.append('../')

ADMINS = (
            ('Benjamin Stookey', 'ben@aashe.org'),
        )
MANAGERS = ADMINS

import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('STARS_DB_URL', None)),
    'iss': dj_database_url.parse(os.environ.get('ISS_DB_URL', None))
}
if 'test' in sys.argv:
    DATABASES['default'] = dj_database_url.parse(os.environ.get('STARS_TEST_DB', None))
    
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

DEFAULT_CHARSET = 'utf-8'

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

# Use a dummy Email Backend for anything but production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# if True, prevents access by non-staff to any part of the site that is not public.
HIDE_REPORTING_TOOL = False
# if True, log-out and re-direct all non-staff requests to standard 503 (Temporarily Unavailable) view.
MAINTENANCE_MODE = False
# This message will be broadcast to all users on every response - usually used to warn about site maintenance
#BROADCAST_MESSAGE = "The STARS reporting tool will be unavailable from mm dd yy hh:mm to hh:mm"
BROADCAST_MESSAGE = None

DEBUG = os.environ.get("DEBUG", False)
TEMPLATE_DEBUG = DEBUG
API_TEST_MODE = DEBUG
# Testing should be true to run test suite - controls other settings and supresses debug output.
TESTING = False
FIXTURE_DIRS = ('fixtures', os.path.join(PROJECT_PATH, 'apps/api/fixtures'),)

TIME_ZONE = 'America/Lima'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/media/admin/'
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
    'stars.apps.accounts.middleware.AuthenticationMiddleware',  # must come after django.contrib.auth.middleware
    'django.middleware.cache.FetchFromCacheMiddleware',
    'stars.apps.accounts.maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'stars.apps.tool.admin.watchdog.middleware.WatchdogMiddleware',  # must come before flatpage so it doesn't log flatpages as 404's
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'stars.apps.helpers.flashMessage.FlashMessageMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
]

CACHE_BACKEND = "dummy://"
CACHE_MIDDLEWARE_SECONDS = 60*15
CACHE_MIDDLEWARE_KEY_PREFIX = "stars"
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

AUTH_PROFILE_MODULE = 'accounts.UserProfile'
AUTHENTICATION_BACKENDS = ('stars.apps.accounts.aashe.AASHEAuthBackend',)
if 'test' in sys.argv:
    AUTHENTICATION_BACKENDS = (
                               'django.contrib.auth.backends.ModelBackend',
                               'stars.apps.accounts.aashe.AASHEAuthBackend',
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
    'django.contrib.admin',
    'django.contrib.redirects',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'stars.apps.credits',
    'stars.apps.tool.credit_editor',
    'stars.apps.tool.my_submission',
    'stars.apps.tool.admin',
    'stars.apps.tool.admin.watchdog',
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
    'aashe.issdjango',
    'south',
    'sorl.thumbnail',
    # 'django_extensions',
    'djcelery',
    'aashe_rules',
    'tastypie',
    'bootstrapform',
    'memcache_status',
)

# Is this running on the django dev server?
STANDALONE_MODE = False

# XML RPC
XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# STARS_DOMAIN is used as part of hash key for securing rpc request.
# WWW_STARS_DOMAIN = "stars.aashe.org"
# #WWW_STARS_DOMAIN = "localhost"
# DEV_STARS_DOMAIN = "stars.dev.aashe.org"
# STAGE_STARS_DOMAIN = "stars.stage.aashe.org"
# STARS_DOMAIN = WWW_STARS_DOMAIN

# SSO_API_KEY is used to authenticate RPC requests
SSO_API_KEY = os.environ.get("SSO_API_KEY", None)
STARS_DOMAIN = os.environ.get("STARS_DOMAIN", "stars.aashe.org")

# ARTICLES module
ARTICLE_PATH_ROOT = "pages"  # defines url / path to articles
ARTICLE_BASE_TERM_ID = 163 # 197 on dev   # tid for base term in Articles taxonomy on IRC

# IRC_DOMAIN is used for 'edit' re-directs on CMS articles
WWW_IRC_DOMAIN = "www.aashe.org"
DEV_IRC_DOMAIN = "dev.aashe.org"
STAGE_IRC_DOMAIN = "stage.aashe.org"
IRC_DOMAIN = WWW_IRC_DOMAIN

SERVICES_PATH = "services/xmlrpc"

SSO_AUTHENTICATION = "xmlrpc:s78dhe3Pm2T"

# Is it possible we may want a different SSO server from the article 'edit' server??
# If not, we should rationalize these two settings.
WWW_SSO_SERVER_URI = "http://%s/%s" % (WWW_IRC_DOMAIN, SERVICES_PATH)
DEV_SSO_SERVER_URI = "http://%s@%s/%s" % (SSO_AUTHENTICATION, DEV_IRC_DOMAIN, SERVICES_PATH)
STAGE_SSO_SERVER_URI = "http://%s@%s/%s" % (SSO_AUTHENTICATION, STAGE_IRC_DOMAIN, SERVICES_PATH)

SSO_SERVER_URI = WWW_SSO_SERVER_URI

# Permissions or user levels for STARS users
STARS_PERMISSIONS = (('admin', 'Administrator'), ('submit', 'Data Entry'), ('view', 'Observer')) # ('review', 'Audit/Review'))

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST", None)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", None)
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'stars_notifier@aashe.org'
EMAIL_REPLY_TO = "stars@aashe.org"

# Celery
import djcelery
djcelery.setup_loader()
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = "sqlite:///tmp/stars-celery-results.db"
CELERY_CACHE_BACKEND = 'dummy'

"""
    Authorize.net credentials
"""
AUTHORIZENET_LOGIN = os.environ.get("AUTHORIZENET_LOGIN", None)
AUTHORIZENET_KEY = os.environ.get("AUTHORIZENET_KEY", None)
AUTHORIZENET_SERVER = os.environ.get("AUTHORIZENET_SERVER", None)

# Debug Toolbar
DEBUG_TOOLBAR = os.environ.get("DEBUG_TOOLBAR", False)
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

"""
    Google Analytics
"""
ANALYTICS_ID = os.environ.get("ANALYTICS_ID", None)

SKIP_SOUTH_TESTS=True

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY", None)
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY", None)

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

if 'test' in sys.argv:
    # until fix for http://code.djangoproject.com/ticket/14105
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.FetchFromCacheMiddleware')
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.UpdateCacheMiddleware')
