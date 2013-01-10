# Default Settings for STARS project
# These can be extended by any .py file in the config folder
import logging, os, sys, django, re
from django.contrib.messages import constants as messages

sys.path.append('../')

ADMINS = (('Benjamin Stookey', 'ben@aashe.org'),('Bob Erb', 'bob.erb@aashe.org'))
MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'

PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

# Use a dummy Email Backend for anything but production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG = os.environ.get("DEBUG", False)
TEMPLATE_DEBUG = DEBUG
API_TEST_MODE = DEBUG
FIXTURE_DIRS = ('fixtures', os.path.join(PROJECT_PATH, 'apps/api/fixtures'),)

TIME_ZONE = 'America/Lima'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('STARS_DB_URL', None)),
    'iss': dj_database_url.parse(os.environ.get('ISS_DB_URL', None))
}
if 'test' in sys.argv:
    DATABASES['default'] = dj_database_url.parse(os.environ.get('STARS_TEST_DB', None))
    DATABASES['default'] = dj_database_url.parse(os.environ.get('ISS_TEST_DB', None))
DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)

# Media
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
STATIC_URL = "/media/static/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", None)

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
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'stars.apps.helpers.flashMessage.FlashMessageMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

AUTH_PROFILE_MODULE = 'accounts.UserProfile'
AUTHENTICATION_BACKENDS = ('stars.apps.accounts.aashe.AASHEAuthBackend',)
if 'test' in sys.argv:
    AUTHENTICATION_BACKENDS = (
                               'django.contrib.auth.backends.ModelBackend',
                               'aashe.aasheauth.backends.AASHEBackend',
                               # 'stars.apps.accounts.aashe.AASHEAuthBackend',
                               )

AASHE_DRUPAL_URI = "http://www.aashe.org/services/xmlrpc"
AASHE_DRUPAL_KEY = "15cf217790e3d45199aeb862f73ab2ff"
AASHE_DRUPAL_KEY_DOMAIN = "acupcc.aashe.org"
AASHE_DRUPAL_COOKIE_SESSION = "SESS0e65dd9c18edb0e7e84759989a5ca2d3"
AASHE_DRUPAL_COOKIE_DOMAIN = ".aashe.org"

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
    'stars.apps.helpers.utils.exception_context',
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
    'aashe.issdjango',
    'south',
    'sorl.thumbnail',
    'django_extensions',
    'djcelery',
    'aashe_rules',
    'tastypie',
    'bootstrapform',
    # 'memcache_status',
    's3_folder_storage',
)

# Is this running on the django dev server?
STANDALONE_MODE = False

# XML RPC
XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# STARS_DOMAIN is used as part of hash key for securing rpc request.
WWW_STARS_DOMAIN = "stars.aashe.org"
#WWW_STARS_DOMAIN = "localhost"
DEV_STARS_DOMAIN = "stars.dev.aashe.org"
STAGE_STARS_DOMAIN = "stars.stage.aashe.org"
STARS_DOMAIN = WWW_STARS_DOMAIN

# SSO_API_KEY is used to authenticate RPC requests
WWW_SSO_API_KEY = "8dca728d46c85b3fda4529692a7f7725"
#WWW_SSO_API_KEY = "e4c8dcfbcb5120ad35b516b04cc35302" # new for localhost
DEV_SSO_API_KEY = "ed9169978073421561d5e90f89f2050e"
STAGE_SSO_API_KEY = "4e9e7e53c571bc48260759963a092522"
SSO_API_KEY = WWW_SSO_API_KEY

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

AASHE_MYSQL_SERVER = "mysql.aashe.net"
AASHE_MYSQL_LOGIN = "starsapp"
AASHE_MYSQL_PASS = "J3z4#$szFET--6"

# Permissions or user levels for STARS users
STARS_PERMISSIONS = (('admin', 'Administrator'), ('submit', 'Data Entry'), ('view', 'Observer')) # ('review', 'Audit/Review'))

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'stars_notifier@aashe.org'
EMAIL_HOST_PASSWORD = 'sustainaashe'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'stars_notifier@aashe.org'
EMAIL_REPLY_TO = "stars@aashe.org"

# sorl thumbnail

#THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_FORMAT = 'PNG'


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

# Authorize.Net
REAL_AUTHORIZENET_LOGIN = "9xaJX497HjE"
REAL_AUTHORIZENET_KEY = "94qx3e7N5h9Xe4WX"
REAL_AUTHORIZENET_SERVER = 'secure.authorize.net'

TEST_AUTHORIZENET_LOGIN = "6t7Jun3QT23"
TEST_AUTHORIZENET_KEY = "7f6k72kXM9yc9Etx"
TEST_AUTHORIZENET_SERVER = 'test.authorize.net'

# default is test mode
AUTHORIZENET_LOGIN = TEST_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = TEST_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = TEST_AUTHORIZENET_SERVER

ANALYTICS_ID = None

SKIP_SOUTH_TESTS=True

RECAPTCHA_PUBLIC_KEY = "6LeaEL0SAAAAAMiipP79s-PzlR0qHlH1-E_jYsyW"
RECAPTCHA_PRIVATE_KEY = "6LeaEL0SAAAAACP5wb3qqxujJc3Cf_qHhVGUr4QV"

GOOGLE_API_KEY = "ABQIAAAA-bTvhmGT1R0ug4p1J_-l4hQWDBNZ3_Sn8d2AByp8vi_J8JN7YxQq-tOQFxf4oNeYJyiW9fXWm-pwNg"

PYTHON_VERSION = None
m = re.match('[\d\.]+', sys.version)
if m:
    PYTHON_VERSION = m.group(0)

DJANGO_VERSION = django.get_version()
HG_REVISION = None

SOUTH_TESTS_MIGRATE = False

# Notes on logging:
#
# 1. Log record formats
#
#    The beginning of each log record has this format;
#
#    {loglevel} {timestamp} "{message}" location={file}:{function}:{linenumber}
#
#    the stars.user logger adds a user element;
#
#    {loglevel} {timestamp} "{message}" location={file}:{function}:{linenumber} \
#        user={user}
#
#    and the stars.request logger adds path, host, and referer elements:
#
#    {loglevel} {timestamp} "{message}" location={file}:{function}:{linenumber} \
#        user={user} path={path} host={host} referer={referer}
#
#    {location} is where the logger was called.
#
#    The {file} part of the location element is usually a path relative to
#    settings.PROJECT_PATH; if it stars with '/', however, it's an absolute
#    path.
#
# 2. Loggers:
#
#    The base logger is named 'stars'.  Use it without any extra context
#    and the file location will added to the log record.
#
#        >>> import logging
#        >>> logger = logging.getLogger('stars')
#        >>> logger.setLevel(logging.INFO)
#        >>> logger.info("Just sayin' hi")
#        INFO 2012-08-07 15:02:07,411 "Just sayin' hi" \
#            location=apps/test/logtest.py:test_stars_log:5
#
#    Use the logger named 'stars.user' if you have a user available
#    and want the username to be inserted into the log message:
#
#        >>> user = User.objects.create(username='jack')
#        >>> logger = logger.getLogger('stars.user')
#        >>> logger.info("Just sayin' hi", extra={'user'=user})
#        INFO 2012-08-07 15:02:07,411 "Just sayin' hi" \
#            location=apps/test/logtest.py:test_stars_log:5 user=Jack
#
#    Use the logger named 'stars.request' if you have a request available
#    and want the log record to have request data inserted into it:
#
#        >>> request = Request.objects.create(path='/crooked/hill', \
#                                             host='reimold', \
#                                             user='Jack', \
#                                             referer='bodette')
#        >>> logger = logger.getLogger('stars.request')
#        >>> logger.info("Just sayin' hi", extra={'request'=request})
#        INFO 2012-08-07 15:02:07,411 "Just sayin' hi" \
#            location=apps/test/logtest.py:test_stars_log:5 user=Jack \
#            path=/crooked/hill host=reimold referer=bodette

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
            'formatter': 'simple_formatter'
        },
        'stars_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stars_formatter'
        },
        'stars_request_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stars_request_formatter'
        },
        'stars_user_console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'stars_user_formatter'
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
