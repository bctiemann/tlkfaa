from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import urllib.request, urllib.error, urllib.parse
import json

import logging
logger = logging.getLogger(__name__)

from sketcher.models import ActiveUser, Drawpile


class Command(BaseCommand):

    def handle(self, *args, **options):

        for drawpile in Drawpile.objects.all():

            drawpile.last_checked_at = timezone.now()
            try:
                response = urllib.request.urlopen('{0}/sessions/'.format(drawpile.admin_url))
                drawpile.is_running = True
                drawpile.save()
            except urllib.error.URLError as e:
                drawpile.is_running = False
                drawpile.status_message = e
                drawpile.save()
                return

            session_data = json.load(response)

            ActiveUser.objects.all().delete()

            for session in session_data:
                if session['title'] == 'Sketcher Reborn':
                    response = urllib.request.urlopen('{0}/sessions/{1}'.format(drawpile.admin_url, session['id']))
                    user_data = json.load(response)
                    online_users = list(filter(lambda user: user['online'], user_data['users']))
                    online_user_names = ', '.join([user['name'] for user in online_users])
                    if online_users:
                        logger.info(f'Drawpile: {online_user_names}')
                    for user in online_users:
                        ActiveUser.objects.create(
                            drawpile=drawpile,
                            name=user['name'],
                            ip=user['ip'],
                            is_op=user.get('op', False),
                            is_mod=user.get('mod', False),
                        )
