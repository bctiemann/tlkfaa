#!/usr/local/bin/bash

# Name of the application
NAME="tlkfaa"

# Django project directory
DJANGODIR=/usr/local/www/django/tlkfaa

# we will communicte using this unix socket
SOCKFILE=/usr/local/www/django/tlkfaa/run/gunicorn.sock

# the user to run as
USER=www

# the group to run as
GROUP=www

# how many worker processes should Gunicorn spawn
NUM_WORKERS=3

# which settings file should Django use
DJANGO_SETTINGS_MODULE=tlkfaa.settings

# WSGI module name
DJANGO_WSGI_MODULE=tlkfaa.wsgi

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR

source ./venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec ./venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=unix:$SOCKFILE \
--log-level=info \
--log-file=-
