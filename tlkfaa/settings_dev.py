try:
    from settings_shared import *
except ImportError:
    pass


DEBUG = False

ALLOWED_HOSTS = ['localhost']

STATIC_ROOT = '/Users/brian.tiemann/Development/tlkfaa-dj/static_root'

MEDIA_ROOT = '/Users/brian.tiemann/Development/tlkfaa-dj/media'

CELERY_TASK_ALWAYS_EAGER = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
