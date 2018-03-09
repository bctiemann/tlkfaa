from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import datetime

import logging
logger = logging.getLogger(__name__)

from fanart import models as models


class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in models.User.objects.exclude(comments=''):
            existing_notes = filter(lambda x: x != '', user.comments.splitlines())
#            print user, existing_notes
            existing_notes[0] = existing_notes[0].replace('/', '-')
            try:
                date_created = datetime.datetime.strptime(existing_notes[0], '%m-%d-%Y')
            except ValueError:
                date_created = datetime.datetime.strptime(existing_notes[0], '%m-%d-%y')
            print user, date_created, existing_notes
            mod_note = models.ModNote.objects.create(
                artist = user,
                note = existing_notes[1],
            )
            mod_note.date_created = date_created
            mod_note.save()
