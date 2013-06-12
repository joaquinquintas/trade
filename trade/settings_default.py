# -*- encoding: utf-8 -*-
import os
from django.conf import global_settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Joaquin Quintas', 'joako84@gmail.com'),

)

MANAGERS = ADMINS

ACCOUNT_ACTIVATION_DAYS = 30

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # Path containing this module

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 1

DEFAULT_FROM_EMAIL = "soporte@intercambio.com"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'djtangosw@gmail.com'
EMAIL_HOST_PASSWORD = 'joaquinlanus3139'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

DEFAULT_CHARSET = 'utf-8'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.abspath(os.path.join( PROJECT_DIR, 'static'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

STATIC_ROOT = os.path.abspath(os.path.join( PROJECT_DIR, 'static'))
STATIC_URL = '/static/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'trade.utils.middleware.AJAXSimpleExceptionResponse',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'trade.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(os.path.join(PROJECT_DIR, 'templates')),

)

LOGIN_REDIRECT_URL = '/cuenta/'

ROSETTA_WSGI_AUTO_RELOAD = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.webdesign',
    'django.contrib.humanize',
    #'django.contrib.admindocs',

    'sorl.thumbnail',
    'tagging',
    #'tagging_ext',
    'haystack',
    'rosetta',
    'media',
    'django_evolution',
    'utils',
    'caching',
    'member',
    'product',
    'transaction',
    'contact',
    'registration',

)

SECRET_KEY = "test"

ugettext = lambda s: s # dummy ugettext function, as said on django docs

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es_AR'

LANGUAGES = (
    ('es_AR', ugettext('Espanol')),
    ('en', ugettext('English')),
)

TRANSMETA_DEFAULT_LANGUAGE = 'es_AR'


# Caching
CACHE_TIMEOUT = 60*10
CACHE_MIDDLEWARE_SECONDS = CACHE_TIMEOUT
CACHE_BACKEND = 'dummy://'
#CACHE_BACKEND = "file://%s?timeout=%s" %  \
#    (os.path.abspath(os.path.join(PROJECT_DIR, 'tmp', 'django_cache')), CACHE_TIMEOUT)
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True


# Thumbnail settings for sorl.thumbnail
THUMBNAIL_PREFIX = '_thumb_'
THUMBNAIL_SUBDIR = '_thumbs'
THUMBNAIL_QUALITY = 85
THUMBNAIL_DEBUG = False

# File Uploads
FILE_UPLOAD_TEMP_DIR = os.path.abspath(os.path.join(PROJECT_DIR, 'tmp'))
FILE_UPLOAD_HANDLERS = ('trade.utils.upload.fileuploadhandler.UploadProgressCachedHandler', ) + \
        global_settings.FILE_UPLOAD_HANDLERS

# Default Markup Filter for trade.utils.markup
MARKUP_FILTER = (None, {})
VISUAL_EDITOR = 'trade.utils.forms.widgets.CKTextEditor'

# Haystack Search
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}