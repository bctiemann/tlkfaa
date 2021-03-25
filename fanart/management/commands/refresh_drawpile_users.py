import json
import logging
from urllib import request, error

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from sketcher.models import ActiveUser, Drawpile

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        for drawpile in Drawpile.objects.all():

            drawpile.last_checked_at = timezone.now()
            try:
                response = request.urlopen(f'{drawpile.admin_url}/sessions/')
                drawpile.is_running = True
                drawpile.save()
            except error.URLError as e:
                drawpile.is_running = False
                drawpile.status_message = e
                drawpile.save()
                return

            session_data = json.load(response)

            ActiveUser.objects.all().delete()

            for session in session_data:
                if session['title'] == settings.DRAWPILE_CHANNEL_NAME:
                    response = request.urlopen(f"{drawpile.admin_url}/sessions/{session['id']}")
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
