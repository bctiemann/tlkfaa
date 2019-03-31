from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re

import logging
logger = logging.getLogger(__name__)

from fanart import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = models.User.objects.all()
        for i, user in enumerate(users):
            print(i, user)
            if not models.ArtistName.objects.filter(artist=user).exists():
                print('Backfilling...')
                artist_name = models.ArtistName.objects.create(artist=user, name=user.username)
                artist_name.date_changed = user.date_joined
                artist_name.save()

