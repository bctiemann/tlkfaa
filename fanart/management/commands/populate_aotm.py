from django.conf import settings
from django.core.management.base import BaseCommand

import os
import unicodedata, re
import datetime
import shutil
from html2bbcode import parser
from PIL import Image

import logging
logger = logging.getLogger(__name__)

from fanart import models
from fanart.utils import unescape


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--map', '--config', default=None,
                        help='Mapping file elements')

    def handle(self, *args, **options):
        bbcode_parser = parser.HTML2BBCode(options.get('map'))

        for artist in models.User.objects.filter(featured__isnull=False).exclude(featured='no').order_by('featured'):
            date_featured = datetime.datetime.strptime(artist.featured, '%Y-%m')
            aotm, created = models.FeaturedArtist.objects.get_or_create(artist=artist, date_featured=date_featured)
            print(aotm)

            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'intro'), 'r')
                aotm.intro_text = unescape(bbcode_parser.feed(re.sub('(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])', ' ', file.read())))
            except IOError:
                pass

            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'ownwords'), 'r')
                aotm.own_words_text = unescape(bbcode_parser.feed(re.sub('(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])', ' ', file.read())))
            except IOError:
                pass

            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'analysis'), 'r')
                aotm.analysis_text = unescape(bbcode_parser.feed(re.sub('(?<![\r\n])(\r?\n|\n?\r)(?![\r\n])', ' ', file.read())))
            except IOError:
                pass

            banner_path = os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'banner.jpg')
            if os.path.exists(banner_path):
                im = Image.open(banner_path)
                aotm.banner = 'featured/{0}/{1}'.format(artist.featured, 'banner.jpg')
                aotm.banner_width = im.width
                aotm.banner_height = im.height
            aotm.save()

            imgs = []
            try:
                file = open(os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured, 'imgs'), 'r')
                imgs = file.readlines()
            except IOError:
                pass

            for img in imgs:
                file_exists = False
                filename = img.rstrip()
                file_dir = os.path.join(settings.MEDIA_ROOT, 'featured', artist.featured)
                file_path = os.path.join(file_dir, filename)
                if os.path.exists(file_path):
                    file_exists = True
                    picture = None
                try:
                    picture = models.Picture.objects.get(artist=artist, filename=filename)
                except models.Picture.DoesNotExist:
                    print('{0} not found'.format(filename))
                except models.Picture.MultipleObjectsReturned:
                    raise Exception('Multiple matches for {0}'.format(filename))

                if picture and not file_exists:
                    if os.path.exists(file_path):
                        raise Exception('{0} already exists in {1}'.format(filename, artist.featured))
                    shutil.copy(picture.path, file_dir)
                    shutil.copy(picture.thumbnail_path, file_dir)

                if os.path.exists(file_path):
                    try:
                        im = Image.open(file_path)
                        width = im.width
                        height = im.height
                    except IOError:
                        width = 0
                        height = 0
                    defaults = {'width': width, 'height': height, 'picture': picture}
                    aotm_pic, created = models.FeaturedArtistPicture.objects.get_or_create(featured_artist=aotm, showcase_picture='featured/{0}/{1}'.format(artist.featured, filename), defaults=defaults)
                    print(aotm_pic)
