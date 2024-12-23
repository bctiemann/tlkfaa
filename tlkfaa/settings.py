"""
Django settings for tlkfaa project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
import yaml
from unipath import Path
from colorlog import ColoredFormatter
from concurrent_log_handler import ConcurrentRotatingFileHandler

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dummy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['fanart-dj.lionking.org', 'fanart.lionking.org']

SERVER_HOST = 'fanart.lionking.org'
SERVER_URL_PREFIX = 'http://'
SERVER_BASE_URL = '{0}{1}'.format(SERVER_URL_PREFIX, SERVER_HOST)

INTERNAL_IPS = [
    '208.178.18.110',
    '23.246.74.58',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'fanart',
    'trading_tree',
    'coloring_cave',
    'pms',
    'artmanager',
    'sketcher',

    'django.contrib.sites.apps.SitesConfig',
#    'django.contrib.humanize.apps.HumanizeConfig',
    'django_nyt.apps.DjangoNytConfig',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki.apps.WikiConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig',
    'wiki.plugins.notifications.apps.NotificationsConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.macros.apps.MacrosConfig',

    'rest_framework',
    # 'debug_toolbar',
    'precise_bbcode',
    'django_extensions',
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tlkfaa.middleware.TimezoneMiddleware',
    'tlkfaa.middleware.XForwardedForMiddleware',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
#STATICFILES_STORAGE = 'fanart.storage.ManifestStaticFilesStorageNonStrict'

ROOT_URLCONF = 'tlkfaa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'sekizai.context_processors.sekizai',
                'fanart.context_processors.settings_constants',
            ],
        },
    },
]

WSGI_APPLICATION = 'tlkfaa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'database.db'),  # Or path to database file if using sqlite3.
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'fanart.User'


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = '/usr/local/www/django/tlkfaa/static_root'
STATIC_URL = '/static/'

MEDIA_ROOT = '/usr/local/www/django/tlkfaa/media'
MEDIA_URL = '/media/'

#MEDIA_URL = '/Artwork/Artists/'

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

# This logging setup has the following attributes:
# When DEBUG = True, debug information will be displayed on requested page.
# It will also show any errors/warnings/info in the console output.
# When DEBUG = False (on production), no debug information will be displayed
# but any errors will be logged in /logs/django.log (project_dir)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'datefmt' : "%d/%b/%Y %H:%M:%S",
            'format': "%(purple)s[%(asctime)s] %(cyan)s[%(name)s:%(lineno)s] %(log_color)s%(levelname)-4s%(reset)s %(white)s%(message)s"
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'logfile': {
            'level':'INFO',
            'filters': [],
            'class':'logging.handlers.ConcurrentRotatingFileHandler',
            'filename': Path(__file__).ancestor(2) + "/logs/django.log",
            'maxBytes': 1024*1024*64, # 64mb
            'backupCount': 5,
            'formatter': 'colored',
        },
    },
    'loggers': {
        '': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'WARN',
            'handlers': ['logfile'],
        }
    },
}


# Debug toolbar nuclear option

def show_toolbar(request):
    return True
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
#    "RESULTS_CACHE_SIZE": 1000,
}

DEBUG_TOOLBAR_PANELS = [
    'ddt_request_history.panels.request_history.RequestHistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
#        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}


SITE_ID = 1

WWW_USER = 'www'

X_FRAME_OPTIONS = 'SAMEORIGIN'

#THUMB_WIDTH = 60
#PREVIEW_WIDTH = 240
ARTIST_RECENT_PICTURES_DAYS = 3
PICTURES_PER_PAGE = 100
PICTURES_PER_PAGE_ARTMANAGER = 20
GIFT_PICTURES_PER_PAGE_ARTMANAGER = 50
CHARACTERS_PER_PAGE_ARTMANAGER = 20
SHOUTS_PER_PAGE_ARTMANAGER = 50
COMMENTS_PER_PAGE_ARTMANAGER = 50
FANS_PER_PAGE_ARTMANAGER = 50
ARTISTS_PER_PAGE = 10
ARTISTS_PER_PAGE_INITIAL = 100
ARTWORK_PER_PAGE = 10
ARTWORK_TOP_RATED_FAVE_CUTOFF = 100
RECENT_UPLOAD_CUTOFF_DAYS = 180
DEFAULT_ARTISTS_VIEW = 'newest'
DEFAULT_ARTWORK_VIEW = 'newest'
DEFAULT_CHARACTERS_VIEW = 'canon'
CHARACTERS_PER_PAGE = 50
PICTURES_PER_CHARACTER_PAGE = 50
PMS_PER_PAGE = 20
MIN_PICTURES_TO_HIDE_GUIDELINES = 2
MIN_PICTURES_FOR_DRAWPILE = 2
MAX_PICTURE_TITLE_CHARS = 750
MAX_UPLOAD_WIDTH = 2000
MAX_UPLOAD_HEIGHT = 2000
MAX_UPLOAD_SIZE = 1048576
APPROVAL_TRIGGER_WIDTH = 1200
APPROVAL_TRIGGER_HEIGHT = 1200
APPROVAL_TRIGGER_SIZE = 307200
APPROVAL_WARNING_WIDTH = 2000
APPROVAL_WARNING_HEIGHT = 2000
APPROVAL_WARNING_SIZE = 307200
MAX_UPLOAD_SIZE_HARD = 15728640
MAX_DRAWPILE_USERS = 12
MAX_BANNER_SIZE = 512000
RECENT_ACTIVITY_CUTOFF_SECS = 300
USER_AGE_BEFORE_COMMENTING_DAYS = 3
FEATURED_ARTWORK_RECENT_YEARS = 3

REVISION_LOG_RECENT_DAYS = 10

# 30th Anniversary banner image (dust swirl effect)
ANNIVERSARY_30 = False

RECAPTCHA_SITE_KEY = None
RECAPTCHA_SECRET_KEY = None
RECAPTCHA_ENABLED = True

# Celery
# CELERY_TASK_SERIALIZER = 'pickle'
# CELERY_RESULT_SERIALIZER = 'pickle'
# CELERY_ACCEPT_CONTENT = ['pickle']
# CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'rpc://'

# Email
EMAIL_HOST = 'mail.lionking.org'
SITE_EMAIL = 'fanart@lionking.org'
DEBUG_EMAIL = 'btman@mac.com'
ADMIN_EMAIL = 'btman@lionking.org'

ADMIN_NAME = 'Brian Tiemann'

ADMINS = [(ADMIN_NAME, DEBUG_EMAIL)]

USE_L10N = False
DATE_FORMAT = 'D n/j/Y'
# DATETIME_FORMAT = 'H:i D n/j/Y'
SHORT_DATE_FORMAT = 'M j, Y'

THUMB_SIZE = {
    'small': 60,
    'large': 240,
    'profile': 200,
    'offer': 120,
}

#CONTENT_TYPE = {
#    'image/jpg': 'jpg',
#    'image/gif': 'gif',
#    'image/png': 'png',
#    'application/x-shockwave-flash"': 'swf',
#    'video/x-ms-wmv': 'wmv',
#    'video/quicktime': 'mov',
#}

PROFILE_TYPES = [
    'image/jpg',
    'image/png',
    'image/gif',
]

IMAGE_FILE_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
}
MOVIE_FILE_TYPES = {
    'application/x-shockwave-flash': 'swf',
    'video/x-ms-wmv': 'wmv',
    'video/x-msvideo': 'avi',
    'video/quicktime': 'mov',
    'video/mpeg': 'mpg',
    'video/mp4': 'mp4',
}

SPINNER_IMG = 'images/loading_spinner.gif'
FAILED_PROCESSING_IMG = 'images/failed_processing.png'
BLANKDOT_IMG = 'images/blankdot.gif'
CHARACTER_PLACEHOLDER_IMG = 'images/blank_characterthumb.jpg'
MOVIE_ICON_IMG = 'images/movie_icon.gif'

SPINNER_IMG_URL = '{0}{1}'.format(STATIC_URL, SPINNER_IMG)
FAILED_PROCESSING_IMG_URL = '{0}{1}'.format(STATIC_URL, FAILED_PROCESSING_IMG)
BLANKDOT_IMG_URL = '{0}{1}'.format(STATIC_URL, BLANKDOT_IMG)
CHARACTER_PLACEHOLDER_IMG_URL = '{0}{1}'.format(STATIC_URL, CHARACTER_PLACEHOLDER_IMG)
MOVIE_ICON_IMG_URL = '{0}{1}'.format(STATIC_URL, MOVIE_ICON_IMG)

BULLETINS_MODERATED = False

DRAWPILE_CHANNEL_NAME = 'Sketcher Reborn'

VERSION = '10.0.4'


# Local overrides from env.yaml
with open(os.path.join(BASE_DIR, 'env.yaml')) as f:
    local_settings = yaml.load(f, Loader=yaml.FullLoader)
globals().update(local_settings)
