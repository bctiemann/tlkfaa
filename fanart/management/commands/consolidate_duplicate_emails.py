from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re

import logging
logger = logging.getLogger(__name__)

from fanart import models as models


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--email',
                    dest='email',
                    default=None,
                    help='Email address to consolidate')

    def handle(self, *args, **options):

        email = options.get('email')

        matching_users = models.User.objects.filter(email=email)
        for user in matching_users:
            print('{is_artist}\
\t{user_id}\
\t{username}\
\t{pic_comments} pic comments\
\t{shouts} shouts\
\t{fave_artists} fave artists\
\t{fave_pics} fave pics\
\t{pictures} pictures\
\t{characters} characters\
\t{folders} folders\
\t{offers} offers\
\t{claims} claims\
\t{gifts_sent} gifts sent\
\t{gifts_rcvd} gifts rcvd\
\t{contest_votes} votes\
'.format(
                is_artist = 'Artist' if user.is_artist else '      ',
                user_id = user.id,
                username = user.username,
                pic_comments = user.picturecomment_set.count(),
                shouts = user.shout_set.count(),
                fave_artists = user.favorite_set.filter(artist__isnull=False).count(),
                fave_pics = user.favorite_set.filter(picture__isnull=False).count(),
                pictures = user.picture_set.count(),
                characters = user.character_set.count(),
                folders = user.folder_set.count(),
                offers = user.offer_set.count(),
                claims = user.claim_set.count(),
                gifts_sent = user.giftpicture_set.count(),
                gifts_rcvd = user.gifts_received.count(),
                contest_votes = user.contestvote_set.count(),
            ))

        master_user_id = int(raw_input('Enter ID of user to consolidate into: '))

        master_user = models.User.objects.get(pk=master_user_id)

        for user in matching_users.exclude(pk=master_user_id):
            print user

            for comment in user.picturecomment_set.all():
                print comment
                print comment.comment
                comment.user = master_user
                comment.save()

            for shout in user.shout_set.all():
                print shout
                print shout.comment
                shout.user = master_user
                shout.save()

            for vote in user.contestvote_set.all():
                vote.user = master_user
                vote.save()

            for fave_artist in user.favorite_set.filter(artist__isnull=False):
                defaults = {
                    'is_visible': fave_artist.is_visible,
                    'date_added': fave_artist.date_added,
                    'last_viewed': fave_artist.last_viewed,
                }
                new_fave, created = models.Favorite.objects.get_or_create(artist=fave_artist.artist, user=master_user, defaults=defaults)
                print new_fave.id, created

            for fave_picture in user.favorite_set.filter(picture__isnull=False):
                defaults = {
                    'is_visible': fave_picture.is_visible,
                    'date_added': fave_picture.date_added,
                    'last_viewed': fave_picture.last_viewed,
                }
                new_fave, created = models.Favorite.objects.get_or_create(picture=fave_picture.picture, user=master_user, defaults=defaults)
                print new_fave.id, created

            print user.absolute_dir_name

            user.delete()

#-Folders: 7
#Featured artist pictures: 8
#-Favorites: 1458
#-Picture comments: 589
#-Shouts: 198
#Picture-tag relationships: 151
#-Characters: 10
#Custom icons: 5
#Contests: 1
#Users: 1
#Bulletins: 4
#-Pictures: 471
#Contest votes: 58
#Unviewed pictures: 121
#-Offers: 2
#-Gift pictures: 227
#-Claims: 6
#Contest entries: 40
#Artist names: 1
#Featured artists: 1
