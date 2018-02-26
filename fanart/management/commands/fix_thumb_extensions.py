from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
from PIL import Image

import logging
logger = logging.getLogger(__name__)

from fanart import models


class Command(BaseCommand):

    def handle(self, *args, **options):

#        for picture in models.Picture.objects.all().order_by('-date_uploaded'):
        for picture in models.Picture.objects.filter(pk=645511).order_by('-date_uploaded'):
            preview = Image.open(picture.preview_path)
            if settings.IMAGE_FILE_TYPES[Image.MIME[preview.format]] != 'jpg':
                print preview.format
                os.rename(picture.preview_path, picture.preview_path_corrected)
            thumbnail = Image.open(picture.thumbnail_path)
            if settings.IMAGE_FILE_TYPES[Image.MIME[thumbnail.format]] != 'jpg':
                print thumbnail.format
                os.rename(picture.thumbnail_path, picture.thumbnail_path_corrected)
