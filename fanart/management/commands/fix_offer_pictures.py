from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os

import logging
logger = logging.getLogger(__name__)

from trading_tree import models


class Command(BaseCommand):

    def handle(self, *args, **options):

        for offer in models.Offer.objects.filter(picture=''):
            print offer
            extension = None
            for ext in ('jpg', 'png', 'gif'):
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'Artwork', 'offers', '{0}.{1}'.format(offer.id, ext))):
                    extension = ext
            if extension:
                offer.picture = 'Artwork/offers/{0}.{1}'.format(offer.id, extension)
                offer.save()
