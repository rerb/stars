# Default Settings for STARS project
# These can be extended by any .py file in the config folder
import os, sys, django, re

sys.path.append('../')

ADMINS = (
            ('Benjamin Stookey', 'ben@aashe.org'),
        )
MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'

# Use a dummy Email Backend for anything but production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# if True, prevents access by non-staff to any part of the site that is not public.
HIDE_REPORTING_TOOL = False  
# if True, log-out and re-direct all non-staff requests to standard 503 (Temporarily Unavailable) view.
MAINTENANCE_MODE = False
# This message will be broadcast to all users on every response - usually used to warn about site maintenance
#BROADCAST_MESSAGE = "The STARS reporting tool will be unavailable from mm dd yy hh:mm to hh:mm"
BROADCAST_MESSAGE = None

DEBUG = False
TEMPLATE_DEBUG = DEBUG
# Testing should be true to run test suite - controls other settings and supresses debug output.
TESTING = False
FIXTURE_DIRS = ('fixtures',)

TIME_ZONE = 'America/Lima'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

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
MANAGE_INSTITUTION_URL = "/tool/manage/"
MANAGE_USERS_URL = MANAGE_INSTITUTION_URL + "users/"
MANAGE_SUBMISSION_SETS_URL = MANAGE_INSTITUTION_URL + "submissionsets/"

ROOT_URLCONF = 'stars.urls'

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), "..", "templates")]

# Use a custom context processor to get all the account and user info
# to the templates
TEMPLATE_CONTEXT_PROCESSORS = (
    "stars.apps.accounts.utils.account_context",
    'stars.apps.helpers.utils.settings_context',
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
    'stars.tests',
    'aashe.issdjango',
    'south',
    'sorl.thumbnail',
    'django_extensions',
    'djcelery',
    # 'memcache_status',
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

# Celery
import djcelery
djcelery.setup_loader()
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

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

#DATABASE_ROUTERS = ('aashe.issdjango.router.ISSRouter',)
PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')

PYTHON_VERSION = None
m = re.match('[\d\.]+', sys.version)
if m:
    PYTHON_VERSION = m.group(0)
    
DJANGO_VERSION = django.get_version()
HG_REVISION = None

SOUTH_TESTS_MIGRATE = False

if os.path.exists(os.path.join(os.path.dirname(__file__), 'hg_info.py')):
    from hg_info import revision
    HG_REVISION = revision

if 'test' in sys.argv:
    # until fix for http://code.djangoproject.com/ticket/14105
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.FetchFromCacheMiddleware')
    MIDDLEWARE_CLASSES.remove('django.middleware.cache.UpdateCacheMiddleware')