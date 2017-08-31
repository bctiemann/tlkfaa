from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import MySQLdb

import logging
logger = logging.getLogger(__name__)

from fanart.models import User


class Command(BaseCommand):

#    all_chars = (unichr(i) for i in xrange(0x110000))
#    control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
#    control_char_re = re.compile('[%s]' % re.escape(control_chars))

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)

    def handle(self, *args, **options):
        db = MySQLdb.connect(passwd='28DcBPP2G6ckhnmXybFR8R25', db='fanart', host='10.0.0.2', user='fadbuser', charset='utf8mb4')

        c = db.cursor(MySQLdb.cursors.DictCursor)
        c.execute("""SELECT * FROM users""")
        for user in c.fetchall():
            print user
            u = User.objects.create_user(
                username = user['username'],
                password = user['passwd'],
                email = user['email'],
                date_joined = user['created'] if user['created'] else timezone.now(),
                last_login = user['lastlogin'],
                last_host = user['lasthost'],
                show_favorite_artists_box = user['showfavoriteartistsbox'],
                show_favorite_pictures_box = user['showfavoritepicturesbox'],
                show_sketcher_box = user['showsketcherbox'],
                show_community_art_box = user['showcommunityartbox'],
                show_contests_box = user['showcontestsbox'],
                show_tool_box = user['showtoolbox'],
                folders_tree = user['folderstree'],
                h_size = user['h_size'],
                v_size = user['v_size'],
            )
            c.execute("""SELECT * FROM artists WHERE userid=%s""", (user['userid'],))
            artist = c.fetchone()
            if artist:
                u.dir_name = artist['dirname']
                u.sort_name = artist['sortname']
                u.is_active = artist['active']
                u.is_enabled = artist['enabled']
                u.is_public = artist['is_public']
                u.is_paid = artist['ispaid'] if artist['ispaid'] != None else True
                u.num_pictures = artist['numpictures']
                u.num_faves = artist['numfaves']
                u.num_favepics = artist['numfavepics']
                u.num_characters = artist['numcharacters']
                u.last_upload = artist['lastupload']
                u.description = artist['artistdesc']
                u.birthday = artist['birthday'] if artist['birthday'] else ''
                u.birth_date = artist['birthdate']
                u.location = artist['location'] if artist['location'] else ''
                u.timezone = artist['timezone'] if artist['timezone'] else ''
                u.occupation = artist['occupation'] if artist['occupation'] else ''
                u.website = artist['website'] if artist['website'] else ''
                u.featured = artist['featured']
                u.comments = artist['comments'] if artist['comments'] else ''
                u.gender = artist['gender']
                u.banner_text = artist['bannertext']
                u.banner_text_updated = artist['bannertextupdated']
                u.banner_text_min = artist['bannertext_min'] if artist['bannertext_min'] else ''
                u.zip_enabled = artist['makezip']
                u.show_email = artist['showemail']
                u.show_birthdate = artist['showbirthdate']
                u.show_birthdate_age = artist['showbirthdate_age']
                u.allow_shouts = artist['allowshouts']
                u.allow_comments = artist['allowcomments']
                u.email_shouts = artist['emailshouts'] if artist['emailshouts'] != None else True
                u.email_comments = artist['emailcomments']
                u.email_pms = artist['emailpms'] if artist['emailpms'] != None else True
                u.show_coloring_cave = artist['showcc']
                u.commissions_open = artist['commissions']
                u.profile_pic_id = artist['profilepic']
                u.profile_pic_ext = artist['profilepic_ext'] if artist['profilepic_ext'] else ''
                u.banner_id = artist['banner']
                u.banner_ext = artist['banner_ext'] if artist['banner_ext'] else ''
                u.suspension_message = artist['suspmessage'] if artist['suspmessage'] else ''
                u.auto_approve = artist['autoapprove']
                u.allow_sketcher = artist['allowsketcher']
                u.sketcher_banned = artist['sketcherbanned']
#                u.sketcher_banned_by = artist['sketcherbannedby']
                u.sketcher_ban_reason = artist['sketcherbanreason'] if artist['sketcherbanreason'] else ''
                u.save()

#            u.id = user['userid']
#            u.save()
