from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os

import logging
logger = logging.getLogger(__name__)

from trading_tree import models


class Command(BaseCommand):

    def handle(self, *args, **options):

        for claim in models.Claim.objects.filter(picture=''):
            print(claim)
            extension = None
            for ext in ('jpg', 'png', 'gif'):
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'Artwork', 'claims', '{0}.{1}'.format(claim.id, ext))):
                    extension = ext
            if extension:
                claim.picture = 'Artwork/claims/{0}.{1}'.format(claim.id, extension)
                claim.save()
