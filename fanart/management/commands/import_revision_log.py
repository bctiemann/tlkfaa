from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone
from django.db.models import Count

import os
import unicodedata, re
import datetime
from html2bbcode import parser

import logging
logger = logging.getLogger(__name__)

from fanart import models as models


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--logfile',
                    dest='logfile',
                    default=None,
                    help='Path of log file to import')
        parser.add_argument('--map', '--config', default=None,
                        help='Mapping file elements')

    def handle(self, *args, **options):

        logfile = options.get('logfile')
        bbcode_parser = parser.HTML2BBCode(options.get('map'))

        reading_data = False

        file = open(logfile, 'r')
        entry = []
        for line in file.read().splitlines():
            if '<DL CLASS="log">' in line:
                reading_data = True

            elif reading_data:
                if '<DT>' in line or '</DL>' in line:
                    if entry != ['']:
                        entry_str = ' '.join(entry)
                        entry_str = entry_str.replace('<br><br>  ', '\n\n').replace('<BR><BR>  ', '\n\n').replace('<DD>', '')
                        entry_str = bbcode_parser.feed(entry_str)
                        print entry_date
                        print entry_str
                        models.RevisionLog.objects.create(date_created=entry_date, entry=entry_str)

                    if '<DT>' in line:
                        entry_date_str = line.replace('<DT>', '')
                        entry_date = datetime.datetime.strptime(entry_date_str, '%B %d, %Y')

                    entry = []
                else:
                    entry.append(line.rstrip())

            elif '</DL>' in line:
                reading_data = False
