# Default Settings for STARS project
# These can be extended by any .py file in the config folder
import os, sys
sys.path.append('../')

ADMINS = (('Benjamin Stookey', 'ben@aashe.org'),('Joseph Fall', 'joseph@aashe.org'))
MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'

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

MEDIA_URL = '/tool/submissions/my_uploads/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

SECRET_KEY = 'omxxweql@m7!@yh5a-)=f^_xo*(m2+gaz#+8dje)e6wv@q$v%@'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'stars.apps.auth.maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'stars.apps.auth.middleware.AuthenticationMiddleware',  # must come after django.contrib.auth.middleware
    'stars.apps.tool.admin.watchdog.middleware.WatchdogMiddleware',  # must come before flatpage so it doesn't log flatpages as 404's
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'stars.apps.helpers.flashMessage.FlashMessageMiddleware',
)

# For in-memory caching, use 'locmem'; During development, use 'dummy' to switch off caching.
#CACHE_BACKEND = "dummy://" 
#CACHE_BACKEND = "locmem://"

AUTHENTICATION_BACKENDS = ('stars.apps.auth.aashe.AASHEAuthBackend',)
# Add the default auth backend so that automated test suite on django.contrib.auth runs correctly.
if TESTING:
    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + ('django.contrib.auth.backends.ModelBackend',)
DASHBOARD_URL = "/tool/"
LOGIN_URL = "/auth/login/"
LOGOUT_URL = "/auth/logout/"
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
    "stars.apps.auth.utils.account_context",
    'stars.apps.auth.utils.tracking_context',
    "django.core.context_processors.auth")

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
	'django.contrib.admin',
    'django.contrib.redirects',
    'django.contrib.flatpages',
	'stars.apps.credits',
	'stars.apps.tool.credit_editor',
	'stars.apps.tool.submissions',
	'stars.apps.tool.admin',
    'stars.apps.tool.admin.watchdog',
	'stars.apps.institutions',
	'stars.apps.registration',
	'stars.apps.submissions',
	'stars.apps.auth',
	'stars.apps.helpers',
    'stars.apps.cms',
	'stars.tests',
)

# Is this running on the django dev server?
STANDALONE_MODE = False

# XML RPC
XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

# STARS_DOMAIN is used as part of hash key for securing rpc request.
WWW_STARS_DOMAIN = "stars.aashe.org"
DEV_STARS_DOMAIN = "stars.dev.aashe.org"
STAGE_STARS_DOMAIN = "stars.stage.aashe.org"
STARS_DOMAIN = WWW_STARS_DOMAIN

# SSO_API_KEY is used to authenticate RPC requests
WWW_SSO_API_KEY = "8dca728d46c85b3fda4529692a7f7725"
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

AASHE_MYSQL_SERVER = "localhost"
AASHE_MYSQL_LOGIN = "starsapp"
AASHE_MYSQL_PASS = "J3z4#$szFET--6"

# Permissions or user levels for STARS users
STARS_PERMISSIONS = (('admin', 'Administrator'), ('submit', 'Data Entry'), ('view', 'Observer')) # ('review', 'Audit/Review'))

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'stars_notifier@aashe.org'
EMAIL_HOST_PASSWORD = 'sustainaashe'
EMAIL_PORT = 587

# CyberSource
CYBERSOURCE_SOAP_KEY = "uIRLgThsKxvp1Fy+/o4xz+Dep/Kur3hvXAHz1mEWyfxZFtSyZG+qMmMGixhXSM+Qltk4PID8H08QAbaqrJMi1yt3g9WWSXHDHMa3MzOChE7GqfdZ7tzGor7H6+5d1mw1ZZwWHTcp0LabEsXIyRVMwTSxCaujF1QU3fAm7hNq530NBmzD/K01DfmWrNj+jjHP4N6n8q6veG9cAfPWYRbJ/FkW1LJkb6oyYwaLGFdIz5CW2Tg8gPwfTxABtqqskyLXK3eD1ZZJccMcxrczM4KETsap91nu3Maivsfr7l3WbDVlnBYdNynQtpsSxcjJFUzBNLEJq6MXVBTd8CbuE2rnfQ=="
CYBERSOURCE_TEST_URL = "https://ics2wstest.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.26.wsdl"
CYBERSOURCE_PRODUCTION_URL = "https://ics2ws.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.26.wsdl"
CYBERSOURCE_MERCHANT_ID = "v2710894"

ANALYTICS_ID = None
