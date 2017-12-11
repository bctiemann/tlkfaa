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
        for showcase in models.Showcase.objects.all():
            print showcase.keyword
            tag = models.Tag.objects.get(tag=showcase.keyword)
            showcase.tag = tag
            showcase.save()
