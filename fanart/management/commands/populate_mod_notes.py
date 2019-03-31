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
            existing_notes = [x for x in user.comments.splitlines() if x != '']
            print(user, existing_notes)
            notes = []
            note = None
            for line in existing_notes:
#                if line[0] in [unicode(x) for x in range(10)]:
#                if len(line) < 11:
                if re.match('^[0-9-/]+$', line):
                    print(len(line))
                    if note:
                        notes.append(note)
                    line = line.replace('/', '-')
                    note = {'date_created': line}
                else:
                    note['note'] = line
            notes.append(note)
            print(notes)
            for note in notes:
                print(note)
                try:
                    date_created = datetime.datetime.strptime(note['date_created'], '%m-%d-%Y')
                except ValueError:
                    date_created = datetime.datetime.strptime(note['date_created'], '%m-%d-%y')
                print(user, date_created, existing_notes)
                mod_note = models.ModNote.objects.create(
                    artist = user,
                    note = note['note'],
                )
                mod_note.date_created = date_created
                mod_note.save()
