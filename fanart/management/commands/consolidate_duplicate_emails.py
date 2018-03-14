from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone
from django.db.models import Count

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
        parser.add_argument('--skip_merge_artists',
                    dest='skip_merge_artists',
                    action='store_true',
                    default=False,
                    help='Skip emails with multiple artist accounts')

    def handle(self, *args, **options):

        email = options.get('email')
        skip_merge_artists = options.get('skip_merge_artists')

        if email:
            email_list = [email]
        else:
            email_list = [u['email'] for u in models.User.objects.values('email').annotate(num_email=Count('email')).filter(num_email__gt=1).order_by('-num_email')]

        print('{0} emails duplicated.'.format(len(email_list)))

        for email in email_list:

            print('')
            print(email)
            matching_users = models.User.objects.filter(email=email)

            valid_user_ids = []
            artist_accounts = []
            for user in matching_users:

                if user.is_artist:
                    artist_accounts.append(user)
                valid_user_ids.append(user.id)
                user_row = '{is_artist}\t{user_id}\t{username}'.format(
                    is_artist = 'Artist' if user.is_artist else '      ',
                    user_id = user.id,
                    username = user.username.encode('utf8'),
                )
                pic_comments = user.picturecomment_set.count()
                shouts = user.shout_set.count()
                fave_artists = user.favorite_set.filter(artist__isnull=False).count()
                fave_pics = user.favorite_set.filter(picture__isnull=False).count()
                contest_votes = user.contestvote_set.count()
                pictures = user.picture_set.count()
                characters = user.character_set.count()
                folders = user.folder_set.count()
                offers = user.offer_set.count()
                claims = user.claim_set.count()
                gifts_sent = user.giftpicture_set.count()
                gifts_rcvd = user.gifts_received.count()

                if pic_comments:
                    user_row += '\t{pic_comments} pic comments'.format(pic_comments=pic_comments)
                if shouts:
                    user_row += '\t{shouts} shouts'.format(shouts=shouts)
                if fave_artists:
                    user_row += '\t{fave_artists} fave artists'.format(fave_artists=fave_artists)
                if fave_pics:
                    user_row += '\t{fave_pics} fave pics'.format(fave_pics=fave_pics)
                if contest_votes:
                    user_row += '\t{contest_votes} votes'.format(contest_votes=contest_votes)
                if pictures:
                    user_row += '\t{pictures} pictures'.format(pictures=pictures)
                if characters:
                    user_row += '\t{characters} characters'.format(characters=characters)
                if folders:
                    user_row += '\t{folders} folders'.format(folders=folders)
                if offers:
                    user_row += '\t{offers} offers'.format(offers=offers)
                if claims:
                    user_row += '\t{claims} claims'.format(claims=claims)
                if gifts_sent:
                    user_row += '\t{gifts_sent} gifts sent'.format(gifts_sent=gifts_sent)
                if gifts_rcvd:
                    user_row += '\t{gifts_rcvd} gifts rcvd'.format(gifts_rcvd=gifts_rcvd)

                print user_row

            if skip_merge_artists and len(artist_accounts) > 1:
                print 'Multiple artist accounts found; skipping'
                continue

            master_user_id_input = raw_input('\nEnter ID of user to consolidate into, or Enter to skip: ')
            if master_user_id_input == '':
                continue

            master_user_id = None
            while master_user_id == None:
                try:
                    master_user_id = int(master_user_id_input)
                    if not master_user_id in valid_user_ids:
                        master_user_id = None
                        raise ValueError
                except ValueError:
                    print 'Invalid input value.'
                    master_user_id_input = raw_input('Enter ID of user to consolidate into, or Enter to skip: ')
                    if master_user_id_input == '':
                        break

            if not master_user_id:
                continue

            master_user = models.User.objects.get(pk=master_user_id)

            for user in matching_users.exclude(pk=master_user_id):
                print user

                for comment in user.picturecomment_set.all():
                    print comment
                    print comment.comment.encode('utf8')
                    comment.user = master_user
                    comment.save()

                for shout in user.shout_set.all():
                    print shout
                    print shout.comment.encode('utf8')
                    shout.user = master_user
                    shout.save()

                for vote in user.contestvote_set.all():
                    vote.user = master_user
                    vote.save()

                for claim in user.claim_set.all():
                    claim.user = master_user
                    claim.save()

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
