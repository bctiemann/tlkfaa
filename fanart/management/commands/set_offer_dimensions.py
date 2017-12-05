from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

from PIL import Image
import os
import unicodedata, re

import logging
logger = logging.getLogger(__name__)

from trading_tree.models import Offer


class Command(BaseCommand):

    def handle(self, *args, **options):
        offers = Offer.objects.filter(picture='')
        for i, offer in enumerate(offers):
            print i, offer
            path = os.path.join(settings.MEDIA_ROOT, 'Artwork', 'offers', '{0}.{1}'.format(offer.id, offer.extension))
            thumb_path = os.path.join(settings.MEDIA_ROOT, 'Artwork', 'offers', '{0}.s.jpg'.format(offer.id))
            img_path = None

            print path
            if os.path.exists(path):
                img_path = path
            elif os.path.exists(thumb_path):
                img_path = thumb_path
            if not img_path:
                continue

            try:
                im = Image.open(img_path)
            except IOError:
                continue

            print im.width, im.height
            offer.width = im.width
            offer.height = im.height
            offer.save()
