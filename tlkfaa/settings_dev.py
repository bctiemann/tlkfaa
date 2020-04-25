try:
    from tlkfaa.settings_shared import *
except ImportError:
    pass


DEBUG = True

ALLOWED_HOSTS = ['localhost']

STATIC_ROOT = '/Users/brian.tiemann/Development/tlkfaa-dj/static_root'

MEDIA_ROOT = '/Users/brian.tiemann/Development/tlkfaa-dj/media'

CELERY_TASK_ALWAYS_EAGER = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_EMAIL = 'fanart@lionking.org'
DEBUG_EMAIL = 'btman@mac.com'
ADMIN_EMAIL = 'btman@mac.com'

RECAPTCHA_ENABLED = False
BULLETINS_MODERATED = False