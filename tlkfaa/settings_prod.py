try:
    from settings_shared import *
except ImportError:
    pass


DEBUG = False

ALLOWED_HOSTS = ['fanart-dj.lionking.org', 'fanart.lionking.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DB_NAME_TLKFAA'],
        'USER': os.environ['DB_USER_TLKFAA'],
        'PASSWORD': os.environ['DB_PASS_TLKFAA'],
        'HOST': os.environ['DB_HOST_TLKFAA'],
        'PORT': os.environ['DB_PORT_TLKFAA'],
        'OPTIONS': {
            'init_command': 'SET character_set_connection=utf8mb4, collation_connection=utf8mb4_general_ci',
            'charset': 'utf8mb4',
        },
    },
}

STATIC_ROOT = '/usr/local/www/django/tlkfaa/static_root'
MEDIA_ROOT = '/usr/local/apache-tomcat-8.0/webapps_fanart/ROOT'

EMAIL_HOST = 'mail.lionking.org'

SITE_EMAIL = 'fanart@lionking.org'
DEBUG_EMAIL = 'btman@mac.com'
ADMIN_EMAIL = 'btman@lionking.org'

ADMINS = [(ADMIN_NAME, ADMIN_EMAIL)]

RECAPTCHA_ENABLED = True

CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']

