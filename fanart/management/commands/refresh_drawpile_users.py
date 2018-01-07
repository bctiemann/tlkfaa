from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import urllib2
import json

import logging
logger = logging.getLogger(__name__)

from sketcher.models import ActiveUser


class Command(BaseCommand):

    base_url = 'http://localhost:8080'

    def handle(self, *args, **options):

        response = urllib2.urlopen('{0}/sessions/'.format(self.base_url))
        session_data = json.load(response)

        ActiveUser.objects.all().delete()

        for session in session_data:
            if session['title'] == 'Sketcher Reborn':
                response = urllib2.urlopen('{0}/sessions/{1}'.format(self.base_url, session['id']))
                user_data = json.load(response)
                for user in user_data['users']:
                    ActiveUser.objects.create(
                        name = user['name'],
                        ip = user['ip'],
                        is_op = user['op'],
                        is_mod = user['mod'],
                    )
