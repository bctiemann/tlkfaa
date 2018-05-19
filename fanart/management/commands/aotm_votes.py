from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone
from django.urls import reverse
from django.db.models import Count

import time

import logging
logger = logging.getLogger(__name__)

from fanart import models, tasks


class Command(BaseCommand):

    def handle(self, *args, **options):

        standings = models.User.objects.filter(featured__isnull=True).values('id', 'username', 'last_login').annotate(num_votes=Count('votes_received')).filter(num_votes__gt=0).order_by('-num_votes')

        for user in standings:
            print('{0}\t{1}\t{2}\t{3}'.format(user['num_votes'], user['last_login'].strftime('%b %d %Y'), user['id'], user['username']))
