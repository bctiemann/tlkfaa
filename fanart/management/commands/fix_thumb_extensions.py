from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
from PIL import Image

import logging
logger = logging.getLogger(__name__)

from fanart import models


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--from_legacy',
                    dest='from_legacy',
                    default=True,
                    action="store_true",
                    help='From legacy (jpg) to corrected (png)')
        parser.add_argument('--to_legacy',
                    dest='to_legacy',
                    default=False,
                    action="store_true",
                    help='From corrected (png) to legacy (jpg)')
        parser.add_argument('--start_id',
                    dest='start_id',
                    default=0,
                    help='Min picture id')

    def handle(self, *args, **options):

        from_legacy = options.get('from_legacy')
        to_legacy = options.get('to_legacy')
        start_id = options.get('start_id')

        for picture in models.Picture.objects.filter(pk__gte=start_id).order_by('-date_uploaded'):
#        for picture in models.Picture.objects.filter(pk=645511).order_by('-date_uploaded'):
            print picture, picture.date_uploaded

            if to_legacy:
                print 'To legacy'
                thumbnail_path = picture.thumbnail_path_corrected
                preview_path = picture.preview_path_corrected
            elif from_legacy:
                print 'From legacy'
                thumbnail_path = picture.thumbnail_path_legacy
                preview_path = picture.preview_path_legacy

            preview = Image.open(preview_path)
            if settings.IMAGE_FILE_TYPES[Image.MIME[preview.format]] != 'jpg':
                print preview.format
                if to_legacy:
                    os.rename(picture.preview_path_corrected, picture.preview_path_legacy)
                elif from_legacy:
                    os.rename(picture.preview_path_legacy, picture.preview_path_corrected)
            thumbnail = Image.open(thumbnail_path)
            if settings.IMAGE_FILE_TYPES[Image.MIME[thumbnail.format]] != 'jpg':
                print thumbnail.format
                if to_legacy:
                    os.rename(picture.thumbnail_path_corrected, picture.thumbnail_path_legacy)
                elif from_legacy:
                    os.rename(picture.thumbnail_path_legacy, picture.thumbnail_path_corrected)
