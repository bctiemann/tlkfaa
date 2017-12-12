from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import datetime
import shutil
from PIL import Image

import logging
logger = logging.getLogger(__name__)

from fanart import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        for artist in models.User.objects.filter(featured__isnull=False).exclude(featured='no').order_by('featured'):
            date_featured = datetime.datetime.strptime(artist.featured, '%Y-%m')
            aotm, created = models.FeaturedArtist.objects.get_or_create(artist=artist, date_featured=date_featured)
            print aotm

            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'intro'), 'r')
                aotm.intro_text = file.read()
            except IOError:
                pass

            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'ownwords'), 'r')
                aotm.own_words_text = file.read()
            except IOError:
                pass

            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'analysis'), 'r')
                aotm.analysis_text = file.read()
            except IOError:
                pass

            aotm.save()

            imgs = []
            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'imgs'), 'r')
                imgs = file.readlines()
            except IOError:
                pass

            for img in imgs:
                filename = img.rstrip()
                file_dir = os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured)
                file_path = os.path.join(file_dir, filename)
                if os.path.exists(file_path):
                    picture = None
                else:
                    try:
                        picture = models.Picture.objects.get(artist=artist, filename=filename)
                    except models.Picture.DoesNotExist:
                        print '{0} not found'.format(filename)
                        continue
                    except models.Picture.MultipleObjectsReturned:
                        raise Exception, 'Multiple matches for {0}'.format(filename)

                if picture:
                    print picture.path
                    if os.path.exists(file_path):
                        raise Exception, '{0} already exists in {1}'.format(filename, artist.featured)
                    shutil.copy(picture.path, file_dir)
                    shutil.copy(picture.thumbnail_path, file_dir)
                else:
                    print file_path

                try:
                    im = Image.open(file_path)
                    width = im.width
                    height = im.height
                except IOError:
                    width = 0
                    height = 0
                defaults = {'width': width, 'height': height}
                aotm_pic, created = models.FeaturedArtistPicture.objects.get_or_create(featured_artist=aotm, picture='featured/{0}/{1}'.format(artist.featured, filename), defaults=defaults)
                print aotm_pic
