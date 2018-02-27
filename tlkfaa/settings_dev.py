try:
    from settings_shared import *
except ImportError:
    pass


DEBUG = True

ALLOWED_HOSTS = ['localhost']

MEDIA_ROOT = '/Users/brian.tiemann/Development/tlkfaa-dj/media'

CELERY_ALWAYS_EAGER = True
