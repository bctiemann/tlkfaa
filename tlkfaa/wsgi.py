"""
WSGI config for tlkfaa project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/usr/local/www/django/tlkfaa')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlkfaa.settings")

#application = get_wsgi_application()

env_variables_to_pass = [
    'DB_NAME_TLKFAA',
    'DB_USER_TLKFAA',
    'DB_PASS_TLKFAA',
    'DB_HOST_TLKFAA',
    'DB_PORT_TLKFAA',
    'DJANGO_SETTINGS_MODULE',
    'SECRET_KEY',
    'RECAPTCHA_SITE_KEY',
    'RECAPTCHA_SECRET_KEY',
]

def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ
    for var in env_variables_to_pass:
        os.environ[var] = environ.get(var, '')
    return get_wsgi_application()(environ, start_response)

