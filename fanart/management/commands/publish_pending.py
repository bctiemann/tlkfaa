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
        requiring_approval = [p.id for p in models.Pending.objects.requiring_approval()]
        for pending in models.Pending.objects.all():
            print pending.id
            if pending.id in requiring_approval:
                print '{0} requires approval'.format(pending.id)
                continue

