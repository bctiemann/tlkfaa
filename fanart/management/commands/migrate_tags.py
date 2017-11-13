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
        pictures = models.Picture.objects.all()
#        pictures = pictures.filter(artist__id=1)
        for i, picture in enumerate(pictures):
            print i, picture
            picture_tags = []
            for keyword in picture.keywords.split(','):
                if keyword:
                    tag, is_created = models.Tag.objects.get_or_create(tag=keyword)
                    print tag, is_created
                    picture_tags.append(tag)
            picture.tags = picture_tags
            picture.save()
