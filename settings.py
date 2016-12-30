import os
import sys
import site
try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

import dj_database_url

import celery
import askbot
from newsboard.periodic_tasks import UPDATE_STREAMS

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

PROJECT_ROOT = os.path.dirname(__file__)
ASKBOT_ROOT = os.path.abspath(os.path.dirname(askbot.__file__))

# Get env vars
ENV_VARS = {
    k.replace('JARDINFAQ_', '').lower(): v
    for k, v in os.environ.items()
    if k.startswith('JARDINFAQ_')
}
# Set default values
DEFAULT_CONFIG = {
    'debug': 'False',
    'template_debug': 'False',
    'server_url': 'jardinfaq.com',
    'allowed_hosts': '*',
    'internal_ips': '127.0.0.1',
    'secret_key': 'fooo',
    'wsgi_application': 'wsgi.application',
    'session_engine': 'django.contrib.sessions.backends.cached_db',
    'log_filename': '/dev/null',
    # Database
    'default_db': 'sqlite:///jardinfaq.sql',
    # Email
    'admins': '',
    'server_email': 'jardinfaq.com',
    'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
    'email_host': 'localhost',
    'email_host_password': '',
    'email_host_user': '',
    'email_port': '25',
    'email_use_tls': 'False',
    'email_use_ssl': 'False',
    'default_from_email': 'equipe@jardinfaq.com',
    'email_subject_prefix': '',
    # Extra files
    'default_file_storage': 'django.core.files.storage.FileSystemStorage',
    'static_url': '/m/',
    'media_url': '/upfiles/',
    'dropbox_oauth2_token': '',
    'static_root': os.path.join(PROJECT_ROOT, 'static/'),
    'media_root': os.path.join(os.path.dirname(__file__), 'askbot', 'upfiles'),
    # Cache
    'cache_backend': 'django_redis.cache.RedisCache',
    'cache_location': 'redis://127.0.0.1:6379:1',
    'cache_option_client_class': 'django_redis.client.DefaultClient',
    # Broker
    'broker_url': 'redis://127.0.0.1:6379:2',
    'broker_transport': 'djkombu.transport.DatabaseTransport',
    'celery_result_backend': 'djcelery.backends.database:DatabaseBackend',
    # Captcha
    'recaptcha_public_key': None,
    'recaptcha_private_key': None,
    'nocaptcha': 'True',
    'recaptcha_use_ssl': 'True',
    'akismet_api_key': None,
    'facebook_token': None,
}

CONFIG_FILE = os.environ.get('JARDINFAQ_CONFIG_FILE',
                             os.path.join(PROJECT_ROOT, 'jardinfaq.cfg'))
CONFIG = SafeConfigParser(defaults=DEFAULT_CONFIG, allow_no_value=True)
CONFIG.read([
    CONFIG_FILE,
    '/etc/jardinfaq.cfg',
    os.path.expanduser('~/.jardinfaq.cfg')
])
map(lambda i: CONFIG.set('DEFAULT', i[0], i[1]),
    ENV_VARS.items())

site.addsitedir(os.path.join(ASKBOT_ROOT, 'deps'))

DEBUG = CONFIG.getboolean('DEFAULT', 'debug')
TEMPLATE_DEBUG = CONFIG.getboolean('DEFAULT', 'template_debug')
ALLOWED_HOSTS = CONFIG.get('DEFAULT', 'allowed_hosts').split(',')
INTERNAL_IPS = CONFIG.get('DEFAULT', 'internal_ips').split(',')
SITE_ID = 1
SECRET_KEY = CONFIG.get('DEFAULT', 'secret_key')

# i18n
LANGUAGE_CODE = 'fr'
LANGUAGES = (('fr', 'French'),)
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True
ASKBOT_LANGUAGE_MODE = 'single-lang'

# Email
ADMINS = CONFIG.get('DEFAULT', 'admins').split(',')
MANAGERS = ADMINS
SERVER_EMAIL = ''
EMAIL_BACKEND = CONFIG.get('DEFAULT', 'email_backend')
EMAIL_HOST = CONFIG.get('DEFAULT', 'email_host')
EMAIL_HOST_PASSWORD = CONFIG.get('DEFAULT', 'email_host_password')
EMAIL_HOST_USER = CONFIG.get('DEFAULT', 'email_host_user')
EMAIL_PORT = CONFIG.getint('DEFAULT', 'email_port')
EMAIL_USE_TLS = CONFIG.getboolean('DEFAULT', 'email_use_tls')
EMAIL_USE_SSL = CONFIG.getboolean('DEFAULT', 'email_use_ssl')
DEFAULT_FROM_EMAIL = CONFIG.get('DEFAULT', 'default_from_email')
EMAIL_SUBJECT_PREFIX = CONFIG.get('DEFAULT', 'email_subject_prefix')

DATABASES = {
    'default': dj_database_url.parse(CONFIG.get('DEFAULT', 'default_db'))
}

# Extra files (CSS, JavaScript, Images)
DEFAULT_FILE_STORAGE = CONFIG.get('DEFAULT', 'default_file_storage')

ASKBOT_EXTRA_SKINS_DIR = os.path.join(PROJECT_ROOT, 'core/skins/')
STATICFILES_DIRS = [
    ASKBOT_EXTRA_SKINS_DIR,
    ('default/media', os.path.join(ASKBOT_ROOT, 'media')),
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATIC_ROOT = CONFIG.get('DEFAULT', 'static_root')
STATIC_URL = CONFIG.get('DEFAULT', 'static_url')

MEDIA_ROOT = CONFIG.get('DEFAULT', 'media_root')
MEDIA_URL = CONFIG.get('DEFAULT', 'media_url')
ADMIN_MEDIA_PREFIX = os.path.join(STATIC_URL, 'admin/')

FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp').replace('\\','/')
FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

# Captcha
RECAPTCHA_PUBLIC_KEY = CONFIG.get('DEFAULT', 'recaptcha_public_key')
RECAPTCHA_PRIVATE_KEY = CONFIG.get('DEFAULT', 'recaptcha_private_key')
NOCAPTCHA = CONFIG.getboolean('DEFAULT', 'nocaptcha')
RECAPTCHA_USE_SSL = CONFIG.getboolean('DEFAULT', 'recaptcha_use_ssl')
AKISMET_API_KEY = CONFIG.get('DEFAULT', 'akismet_api_key')


TEMPLATES = (
    {
        'BACKEND': 'askbot.skins.template_backends.AskbotSkinTemplates',
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    },
)

MIDDLEWARE_CLASSES = [
    #'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    ## Enable the following middleware if you want to enable
    ## language selection in the site settings.
    #'askbot.middleware.locale.LocaleMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.sqlprint.SqlPrintingMiddleware',

    #below is askbot stuff for this tuple
    'askbot.middleware.anon_user.ConnectToSessionMessagesMiddleware',
    'askbot.middleware.forum_mode.ForumModeMiddleware',
    'askbot.middleware.cancel.CancelActionMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'askbot.middleware.view_log.ViewLogMiddleware',
    'askbot.middleware.spaceless.SpacelessMiddleware',
    'askbot.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middlewares.UserBasedExceptionMiddleware',
]

ATOMIC_REQUESTS = True

ROOT_URLCONF = 'urls'

ASKBOT_ALLOWED_UPLOAD_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png',)
ASKBOT_MAX_UPLOAD_FILE_SIZE = 1024 * 1024

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # All of these are needed for the askbot
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'core',
    'compressor',
    'askbot',
    'askbot.deps.django_authopenid',
    #'askbot.importers.stackexchange', #se loader
    'askbot.deps.livesettings',
    'keyedcache',
    'robots',
    'django_countries',
    'djcelery',
    'djkombu',
    'followit',
    'tinymce',
    'askbot.deps.group_messaging',
    #'avatar',#experimental use git clone git://github.com/ericflo/django-avatar.git$
    'captcha',
    'avatar',
    'core.facebook_sync',
    'favicon',
    'dbbackup',
    'dj_web_rich_object',
    'newsboard',
]

CACHES = {
    'default': {
        'BACKEND': CONFIG.get('DEFAULT', 'cache_backend'),
        'LOCATION': CONFIG.get('DEFAULT', 'cache_location'),
        'TIMEOUT': 6000,
        'KEY_PREFIX': 'askbot',
        'OPTIONS': {
            'CLIENT_CLASS': CONFIG.get('DEFAULT', 'cache_option_client_class')
        }
    }
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Sets a special timeout for livesettings if you want to make them different
LIVESETTINGS_CACHE_TIMEOUT = CACHES['default']['TIMEOUT']
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 600


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'askbot.deps.django_authopenid.backends.AuthBackend',
)

#logging settings
# LOG_FILENAME = CONFIG.get('DEFAULT', 'log_filename')
# logging.basicConfig(
#     filename=LOG_FILENAME,
#     level=logging.CRITICAL,
#     format='%(pathname)s TIME: %(asctime)s MSG: %(filename)s:%(funcName)s:%(lineno)d %(message)s',
# )

ASKBOT_URL = ''
ASKBOT_TRANSLATE_URL = True
_ = lambda v: v  #fake translation function for the login url
LOGIN_URL = '/%s%s%s' % (ASKBOT_URL, _('account/'), _('signin/'))
LOGIN_REDIRECT_URL = ASKBOT_URL
ALLOW_UNICODE_SLUGS = False
ASKBOT_USE_STACKEXCHANGE_URLS = False

#Celery Settings
CELERY_BROKER_URL = BROKER_URL = CONFIG.get('DEFAULT', 'broker_url')
CELERY_BROKER_TRANSPORT = BROKER_TRANSPORT = CONFIG.get('DEFAULT', 'broker_transport')
CELERY_RESULT_BACKEND = CONFIG.get('DEFAULT', 'celery_result_backend')
CELERY_ALWAYS_EAGER = False

import djcelery
djcelery.setup_loader()
DOMAIN_NAME = ''

CSRF_COOKIE_NAME = '_csrf'

NOCAPTCHA = True

#HAYSTACK_SETTINGS
ENABLE_HAYSTACK_SEARCH = False
#Uncomment for multilingual setup:
#HAYSTACK_ROUTERS = ['askbot.search.haystack.routers.LanguageRouter',]

#Uncomment if you use haystack
#More info in http://django-haystack.readthedocs.org/en/latest/settings.html
#HAYSTACK_CONNECTIONS = {
#            'default': {
#                        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
#            }
#}

TINYMCE_COMPRESSOR = True
TINYMCE_SPELLCHECKER = False
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'default/media/tinymce/')
#TINYMCE_JS_URL = STATIC_URL + 'default/media/tinymce/tiny_mce.js'
TINYMCE_DEFAULT_CONFIG = {
    'editor_deselector': 'mceNoEditor',
    'plugins': 'askbot_imageuploader,askbot_attachment',
    'convert_urls': False,
    'theme': 'advanced',
    'content_css': os.path.join(STATIC_URL, 'default/media/style/tinymce/content.css'),
    'force_br_newlines': True,
    'force_p_newlines': False,
    'forced_root_block': '',
    'mode': 'textareas',
    'oninit': "TinyMCE.onInitHook",
    'plugins': 'askbot_imageuploader,askbot_attachment',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_toolbar_align': 'left',
    'theme_advanced_buttons1': 'bold,italic,underline,|,bullist,numlist,|,undo,redo,|,link,unlink,askbot_imageuploader,askbot_attachment',
    'theme_advanced_buttons2': '',
    'theme_advanced_buttons3': '',
    'theme_advanced_path': False,
    'theme_advanced_resizing': True,
    'theme_advanced_resize_horizontal': False,
    'theme_advanced_statusbar_location': 'bottom',
    'width': '730',
    'height': '250'
}

# delayed notifications, time in seconds, 15 mins by default
NOTIFICATION_DELAY_TIME = 60 * 10

GROUP_MESSAGING = {
    'BASE_URL_GETTER_FUNCTION': 'askbot.models.user_get_profile_url',
    'BASE_URL_PARAMS': {'section': 'messages', 'sort': 'inbox'}
}


ASKBOT_CSS_DEVEL = False
if 'ASKBOT_CSS_DEVEL' in locals() and ASKBOT_CSS_DEVEL:
    COMPRESS_PRECOMPILERS = (
        ('text/less', 'lessc {infile} {outfile}'),
    )

COMPRESS_JS_FILTERS = []
COMPRESS_PARSER = 'compressor.parser.HtmlParser'
JINJA2_EXTENSIONS = (
    'compressor.contrib.jinja2ext.CompressorExtension',
)
JINJA2_TEMPLATES = ('captcha',)

VERIFIER_EXPIRE_DAYS = 3
AVATAR_AUTO_GENERATE_SIZES = (16, 32, 48, 128)

DBBACKUP_HOSTNAME = 'jardinfaq'
DBBACKUP_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'oauth2_access_token': CONFIG.get('DEFAULT', 'dropbox_oauth2_token')
}


def add_debug_toolbar():
    try:
        __import__('imp').find_module('debug_toolbar')
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        TEMPLATES[1]['OPTIONS']['context_processors'].insert(
            0, 'django.template.context_processors.debug')
    except ImportError:
        pass

if DEBUG:
    add_debug_toolbar()

ASKBOT_MIN_DAYS_TO_ANSWER_OWN_QUESTION = 0
ASKBOT_LIMIT_ONE_ANSWER_PER_USER = False
ASKBOT_MARKDOWN_CLASS = 'core.markdown.Markdown'
ASKBOT_EXTRA_ACCEPTABLE_ATTRIBUTES = ('id', 'data-image', 'data-description')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
         },
         'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
         },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

NEWSBOARD_FACEBOOK_TOKEN = CONFIG.get('DEFAULT', 'facebook_token')

if celery.VERSION < (4, 0, 0):
    CELERYBEAT_SCHEDULE = {
        'auto-update-streams': UPDATE_STREAMS
    }
print DATABASES
