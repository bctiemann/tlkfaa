from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import MySQLdb

import logging
logger = logging.getLogger(__name__)

from fanart import models as fanart_models
from trading_tree.models import Offer, Claim
from coloring_cave.models import Base, ColoringPicture
from pms.models import PrivateMessage


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)

    def handle(self, *args, **options):
        db = MySQLdb.connect(passwd='28DcBPP2G6ckhnmXybFR8R25', db='fanart', host='10.0.0.2', user='fadbuser', charset='utf8mb4')
        c = db.cursor(MySQLdb.cursors.DictCursor)

        count = 0
        for user in fanart_models.User.objects.filter(artist_id_orig__isnull=False):
            c.execute("""SELECT * FROM artists WHERE artistid=%s""", (user.artist_id_orig,))
            for old_artist in c.fetchall():
                if old_artist['email'] and user.email != old_artist['email']:
                    print user
                    print old_artist['email'].encode('utf8')
                    count += 1

#                    replace_input = raw_input('\nUpdate email to {0} ? '.format(old_artist['email'].encode('utf8')))
#                    if replace_input.lower() == 'y':
                    if True:
                        print('Replacing')
                        user.email = old_artist['email']
                        user.save()
                    else:
                        print('Skipping')
                    print('')
        print count
