from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import MySQLdb

import logging
logger = logging.getLogger(__name__)

from fanart.models import User, Folder, Picture, PictureComment, Shout, ColoringBase, ColoringPicture, Character


class Command(BaseCommand):

#    all_chars = (unichr(i) for i in xrange(0x110000))
#    control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
#    control_char_re = re.compile('[%s]' % re.escape(control_chars))

    do_users = False
    do_folders = False
    do_pictures = False
    do_comments = False
    do_shouts = False
    do_coloringbase = False
    do_coloringpics = True
    do_characters = False

    GENDERS = {
        0: 'neither',
        1: 'male',
        2: 'female',
    }

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)

    def get_child_folders(self, c, folder_id, new_folder):
        if folder_id:
            c.execute("""SELECT * FROM folders WHERE parent=%s""", (folder_id,))
        else:
            c.execute("""SELECT * FROM folders WHERE parent is null""")
        for folder in c.fetchall():
            print folder
            f = None
            try:
                user = User.objects.get(artist_id_orig=folder['artistid'])
                print user
                f = Folder.objects.create(
                    id_orig = folder['folderid'],
                    user = user,
                    name = folder['name'],
                    description = folder['description'],
                    parent = new_folder,
                )
            except User.DoesNotExist:
                pass
            self.get_child_folders(c, folder['folderid'], f)

    def get_child_comments(self, c, comment_id, new_comment):
        if comment_id:
            c.execute("""SELECT * FROM comments WHERE replyto=%s""", (comment_id,))
        else:
            c.execute("""SELECT * FROM comments WHERE replyto is null""")
        for comment in c.fetchall():
            print comment
            f = None
            try:
                user = User.objects.get(id_orig=comment['userid'])
                print user
                picture = Picture.objects.get(id_orig=comment['pictureid'])
                print picture
                f = PictureComment.objects.create(
                    id_orig = comment['commentid'],
                    user = user,
                    picture = picture,
                    comment = comment['comment'],
                    reply_to = new_comment,
                    date_posted = comment['posted'],
                    date_edited = comment['edited'],
                    is_deleted = comment['deleted'],
                    is_received = comment['viewed'],
                    hash = comment['hash'],
                )
            except User.DoesNotExist:
                pass
            except Picture.DoesNotExist:
                pass
            self.get_child_comments(c, comment['commentid'], f)

    def handle(self, *args, **options):
        db = MySQLdb.connect(passwd='28DcBPP2G6ckhnmXybFR8R25', db='fanart', host='10.0.0.2', user='fadbuser', charset='utf8mb4')
        c = db.cursor(MySQLdb.cursors.DictCursor)

        if self.do_users:
            c.execute("""SELECT * FROM users""")
            for user in c.fetchall():
                print user
                u = User.objects.create_user(
                    id_orig = user['userid'],
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
                    u.artist_id_orig = artist['artistid']
                    u.dir_name = artist['dirname']
                    u.sort_name = artist['sortname']
                    u.is_active = artist['active']
                    u.is_enabled = artist['enabled']
                    u.is_public = artist['is_public'] if artist['is_public'] != None else True
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
                    u.gender = artist['gender'] if artist['gender'] else ''
                    u.banner_text = artist['bannertext']
                    u.banner_text_updated = artist['bannertextupdated']
                    u.banner_text_min = artist['bannertext_min'] if artist['bannertext_min'] else ''
                    u.zip_enabled = artist['makezip'] if artist['makezip'] != None else True
                    u.show_email = artist['showemail'] if artist['showemail'] != None else True
                    u.show_birthdate = artist['showbirthdate'] if artist['showbirthdate'] != None else True
                    u.show_birthdate_age = artist['showbirthdate_age'] if artist['showbirthdate_age'] != None else True
                    u.allow_shouts = artist['allowshouts'] if artist['allowshouts'] != None else True
                    u.allow_comments = artist['allowcomments'] if artist['allowcomments'] != None else True
                    u.email_shouts = artist['emailshouts'] if artist['emailshouts'] != None else True
                    u.email_comments = artist['emailcomments'] if artist['emailcomments'] != None else True
                    u.email_pms = artist['emailpms'] if artist['emailpms'] != None else True
                    u.show_coloring_cave = artist['showcc'] if artist['showcc'] != None else True
                    u.commissions_open = artist['commissions'] if artist['commissions'] != None else True
                    u.profile_pic_id = artist['profilepic']
                    u.profile_pic_ext = artist['profilepic_ext'] if artist['profilepic_ext'] else ''
                    u.banner_id = artist['banner']
                    u.banner_ext = artist['banner_ext'] if artist['banner_ext'] else ''
                    u.suspension_message = artist['suspmessage'] if artist['suspmessage'] else ''
                    u.auto_approve = artist['autoapprove']
                    u.allow_sketcher = artist['allowsketcher']
                    u.sketcher_banned = artist['sketcherbanned']
#                    u.sketcher_banned_by = artist['sketcherbannedby']
                    u.sketcher_ban_reason = artist['sketcherbanreason'] if artist['sketcherbanreason'] else ''
                    u.save()

        if self.do_folders:
            self.get_child_folders(c, None, None)

        if self.do_pictures:
            c.execute("""SELECT * FROM pictures""")
            for picture in c.fetchall():
                print picture
                try:
                    user = User.objects.get(artist_id_orig=picture['artistid'])

                    try:
                        folder = Folder.objects.get(id_orig=picture['folderid'])
                    except Folder.DoesNotExist:
                        folder = None

                    try:
                        approver = User.objects.get(id_orig=picture['insertedby'])
                    except User.DoesNotExist:
                        approver = None

                    p = Picture.objects.create(
                        id_orig = picture['pictureid'],
                        artist = user,
                        folder = folder,
                        filename = picture['filename'],
                        extension = picture['extension'],
                        title = picture['title'],
                        is_color = picture['color'],
                        type = picture['type'],
                        mime_type = picture['mimetype'],
                        file_size = picture['filesize'],
                        quality = picture['quality'] if picture['quality'] else '',
                        thumb_height = picture['thumbheight'],
                        num_comments = picture['numcomments'],
                        num_faves = picture['numpicfaves'],
                        characters = picture['characters'] if picture['characters'] else '',
                        width = picture['width'],
                        height = picture['height'],
                        date_uploaded = picture['uploaded'],
                        date_approved = picture['inserted'],
                        date_updated = picture['updated'],
                        date_deleted = picture['deleted'],
                        hash = picture['hash'],
                        is_public = picture['picpublic'],
                        rank_in_artist = picture['rankinartist'],
                        rank_in_folder = picture['rankinfolder'],
                        approved_by = approver,
                        keywords = picture['keywords'],
                        work_in_progress = picture['wip'],
                        allow_comments = picture['allowcomments_p'],
                        is_scanned = picture['scanned'],
                        needs_poster = picture['needs_poster'] if picture['needs_poster'] != None else False,
                    )
                except User.DoesNotExist:
                    pass

        if self.do_comments:
            self.get_child_comments(c, None, None)

        if self.do_shouts:
            c.execute("""SELECT * FROM shouts""")
            for comment in c.fetchall():
                print comment
                f = None
                try:
                    user = User.objects.get(id_orig=comment['userid'])
                    print user
                    artist = User.objects.get(id_orig=comment['artistid'])
                    print artist
                    f = Shout.objects.create(
                        id_orig = comment['shoutid'],
                        user = user,
                        artist = artist,
                        comment = comment['comment'],
                        date_posted = comment['posted'],
                        date_edited = comment['edited'],
                        is_deleted = comment['deleted'],
                        is_received = comment['viewed'],
                    )
                except User.DoesNotExist:
                    pass

        if self.do_coloringbase:
            c.execute("""SELECT * FROM coloring_base""")
            for cb in c.fetchall():
                print cb
                try:
                    creator = User.objects.get(id_orig=cb['artistid'])
                    print creator
                    picture = Picture.objects.get(id_orig=cb['pictureid'])
                    print picture
                    f = ColoringBase.objects.create(
                        id_orig = cb['coloring_baseid'],
                        creator = creator,
                        picture = picture,
                        date_posted = cb['posted'],
                        is_active = cb['active'],
                        is_visible = cb['visible'],
                        num_colored = cb['numcolored'],
                    )
                except User.DoesNotExist:
                    pass
                except Picture.DoesNotExist:
                    pass

        if self.do_coloringpics:
            c.execute("""SELECT * FROM coloring_pics""")
            for cp in c.fetchall():
                print cp
                try:
                    artist = User.objects.get(id_orig=cp['artistid'])
                    print artist
                    base = ColoringBase.objects.get(id_orig=cp['basepic'])
                    print base
                    f = ColoringPicture.objects.create(
                        id_orig = cp['coloring_picid'],
                        artist = artist,
                        base = base,
                        date_posted = cp['posted'],
                        comment = cp['comment'],
                        picture = cp['filename'],
                        extension = cp['extension'],
                        width = cp['width'],
                        height = cp['height'],
                        thumb_height = cp['thumbheight'],
                    )
                except User.DoesNotExist:
                    pass
                except ColoringBase.DoesNotExist:
                    pass
