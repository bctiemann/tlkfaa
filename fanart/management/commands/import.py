import MySQLdb
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from fanart import models as fanart_models
from trading_tree.models import Offer, Claim
from coloring_cave.models import Base, ColoringPicture
from pms.models import PrivateMessage

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    enabled = {
       # 'do_users': True,
       # 'do_folders': True,
       # 'do_pictures': True,
       # 'do_comments': True,
       # 'do_shouts': True,
       # 'do_coloringbase': True,
       # 'do_coloringpics': True,
       # 'do_characters': True,
       # 'do_favorites': True,
       # 'do_offers': True,
       # 'do_claims': True,
       # 'do_picturecharacters': True,
       # 'do_tags': True,
       # 'do_approvers': True,
       # 'do_sketcheradmins': True,
        'do_requests': True,
       # 'do_imclients': True,
       # 'do_imids': True,
       # 'do_newpics': True,
       # 'do_approval_access': True,
       # 'do_adminblog': True,
       # 'do_artistnames': True,
       # 'do_blocks': True,
       # 'do_bulletins': True,
       # 'do_contests': True,
       # 'do_contestpics': True,
       # 'do_contestvotes': True,
       # 'do_pms': True,
       # 'do_specials': True,
       # 'do_votes': True,
       # 'do_customicons': True,
    }

    GENDERS = {
        0: '',
        1: 'male',
        2: 'female',
        3: '',
    }

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)

    def get_child_folders(self, c, folder_id, new_folder):
        if folder_id:
            c.execute("""SELECT * FROM folders WHERE parent=%s""", (folder_id,))
        else:
            c.execute("""SELECT * FROM folders WHERE parent is null""")
        for folder in c.fetchall():
            print(folder)
            f = None
            try:
                user = fanart_models.User.objects.get(artist_id_orig=folder['artistid'])
                print(user)
                f = fanart_models.Folder.objects.create(
                    id_orig = folder['folderid'],
                    id = folder['folderid'],
                    user = user,
                    name = folder['name'],
                    description = folder['description'],
                    parent = new_folder,
                )
            except fanart_models.User.DoesNotExist:
                pass
            self.get_child_folders(c, folder['folderid'], f)

    def get_child_comments(self, c, comment_id, new_comment):
        if comment_id:
            c.execute("""SELECT * FROM comments WHERE replyto=%s""", (comment_id,))
        else:
            c.execute("""SELECT * FROM comments WHERE replyto is null""")
        for comment in c.fetchall():
            print(comment)
            f = None
            try:
                user = None
                if comment['userid']:
                    user = fanart_models.User.objects.get(id_orig=comment['userid'])
                print(user)
                picture = fanart_models.Picture.objects.get(id_orig=comment['pictureid'])
                print(picture)
                f = fanart_models.PictureComment.objects.create(
                    id_orig = comment['commentid'],
                    id = comment['commentid'],
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
                f.date_posted = comment['posted']
                f.save()
            except fanart_models.User.DoesNotExist:
                pass
            except fanart_models.Picture.DoesNotExist:
                pass
            self.get_child_comments(c, comment['commentid'], f)

    def get_child_pms(self, c, pm_id, new_pm):
        c.execute("""SELECT * FROM pms WHERE replyto=%s""", (pm_id,))
        for pm in c.fetchall():
            print(pm)
            f = None
            try:
                sender = fanart_models.User.objects.get(id_orig=pm['senderid'])
                recipient = fanart_models.User.objects.get(id_orig=pm['recptid'])
                f = PrivateMessage.objects.create(
                    id = pm['pmid'],
                    sender = sender,
                    recipient = recipient,
                    date_sent = pm['sent'],
                    reply_to = new_pm,
                    subject = pm['subject'],
                    message = pm['message'],
                    date_viewed = timezone.now() if pm['viewed'] else None,
                    date_replied = timezone.now() if pm['replied'] else None,
                    deleted_by_sender = pm['deleted_s'],
                    deleted_by_recipient = pm['deleted_r'],
                )
                f.date_sent = pm['sent']
                f.save()
            except fanart_models.User.DoesNotExist:
                pass
            self.get_child_pms(c, pm['pmid'], f)


    def handle(self, *args, **options):
        db = MySQLdb.connect(
            passwd=settings.DATABASES['legacy']['PASSWORD'],
            db=settings.DATABASES['legacy']['NAME'],
            host=settings.DATABASES['legacy']['HOST'],
            user=settings.DATABASES['legacy']['USER'],
            charset=settings.DATABASES['legacy']['OPTIONS']['charset'],
        )
        c = db.cursor(MySQLdb.cursors.DictCursor)

        if 'do_users' in self.enabled:
#            c.execute("""SELECT * FROM users where userid=1""")
#            c.execute("""SELECT * FROM users""")
#            for user in c.fetchall():
            for user in []:
                print(user)
                u = fanart_models.User.objects.create_user(
                    id_orig = user['userid'],
                    id = user['userid'],
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
                    is_artist = False,
                )
                u.date_joined = user['created'] if user['created'] else timezone.now()
                u.password = user['passwd']
                u.save()
#            c.execute("""SELECT * FROM artists WHERE userid=%s""", (user.id,))
#            c.execute("""SELECT * FROM artists""")
            c.execute("""SELECT * FROM artists where artistid=955""")
#            artist = c.fetchone()
            for artist in c.fetchall():
                if artist['userid']:
                    u, created = fanart_models.User.objects.get_or_create(id=artist['userid'])
                else:
                    u, created = fanart_models.User.objects.get_or_create(username=artist['artistname'])
                print(u)
                u.artist_id_orig = artist['artistid']
                u.dir_name = artist['dirname'] if artist['dirname'] else ''
                u.sort_name = artist['sortname'] if artist['sortname'] else ''
                u.is_active = artist['enabled']
                u.is_artist = artist['active']
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
                u.gender = self.GENDERS[artist['gender']] if artist['gender'] else ''
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
                u.old_banner_id = artist['banner']
                u.old_banner_ext = artist['banner_ext'] if artist['banner_ext'] else ''
                u.suspension_message = artist['suspmessage'] if artist['suspmessage'] else ''
                u.auto_approve = artist['autoapprove']
                u.allow_sketcher = artist['allowsketcher']
                u.sketcher_banned = artist['sketcherbanned']
#                u.sketcher_banned_by = artist['sketcherbannedby']
                u.sketcher_ban_reason = artist['sketcherbanreason'] if artist['sketcherbanreason'] else ''
                u.save()

                if artist['created']:
                    u.date_joined = artist['created']
                    u.save()

        if 'do_folders' in self.enabled:
            self.get_child_folders(c, None, None)

        if 'do_pictures' in self.enabled:
            c.execute("""SELECT * FROM pictures""")
            for picture in c.fetchall():
                print(picture)
                try:
                    user = fanart_models.User.objects.get(artist_id_orig=picture['artistid'])

                    try:
                        folder = fanart_models.Folder.objects.get(id_orig=picture['folderid'])
                    except fanart_models.Folder.DoesNotExist:
                        folder = None
                        print('No folder')

                    approver = None
                    if picture['insertedby']:
                        try:
                            approver = fanart_models.User.objects.get(id_orig=picture['insertedby'])
                        except fanart_models.User.DoesNotExist:
                            approver = None
                            print('No approver')

                    p = fanart_models.Picture.objects.create(
                        id_orig = picture['pictureid'],
                        id = picture['pictureid'],
                        artist = user,
                        folder = folder,
                        filename = picture['filename'],
#                        extension = picture['extension'],
                        title = picture['title'],
                        is_color = picture['color'],
                        type = picture['type'],
                        mime_type = picture['mimetype'],
                        file_size = picture['filesize'],
                        quality = picture['quality'] if picture['quality'] else '',
#                        thumb_height = picture['thumbheight'],
                        num_comments = picture['numcomments'],
                        num_faves = picture['numpicfaves'],
#                        characters = picture['characters'] if picture['characters'] else '',
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
                        watchers_notified = True,
                    )
                except fanart_models.User.DoesNotExist:
                    pass
                    print('No artist')

        if 'do_comments' in self.enabled:
            self.get_child_comments(c, None, None)

        if 'do_shouts' in self.enabled:
            c.execute("""SELECT * FROM shouts""")
            for comment in c.fetchall():
                print(comment)
                f = None
                try:
                    user = fanart_models.User.objects.get(id_orig=comment['userid'])
                    print(user)
                    artist = fanart_models.User.objects.get(artist_id_orig=comment['artistid'])
                    print(artist)
                    f = fanart_models.Shout.objects.create(
                        id_orig = comment['shoutid'],
                        id = comment['shoutid'],
                        user = user,
                        artist = artist,
                        comment = comment['comment'],
                        date_posted = comment['posted'],
                        date_edited = comment['edited'],
                        is_deleted = comment['deleted'],
                        is_received = comment['viewed'],
                    )
                    f.date_posted = comment['posted']
                    f.save()
                except fanart_models.User.DoesNotExist:
                    pass

        if 'do_coloringbase' in self.enabled:
#            c.execute("""SELECT * FROM coloring_base where coloring_baseid = 2655""")
            c.execute("""SELECT * FROM coloring_base""")
            for cb in c.fetchall():
                print(cb)
                try:
                    creator = fanart_models.User.objects.get(artist_id_orig=cb['artistid'])
                    print(creator)
                    picture = fanart_models.Picture.objects.get(id_orig=cb['pictureid'])
                    print(picture)
                    f = Base.objects.create(
                        id_orig = cb['coloring_baseid'],
                        id = cb['coloring_baseid'],
                        creator = creator,
                        picture = picture,
#                        date_posted = cb['posted'],
                        is_active = cb['active'],
                        is_visible = cb['visible'],
                        num_colored = cb['numcolored'],
                    )
                    f.date_posted = cb['posted']
                    f.save()
                except fanart_models.User.DoesNotExist:
                    print('Artist not found')
                    pass
                except fanart_models.Picture.DoesNotExist:
                    print('Picture not found')
                    pass

        if 'do_coloringpics' in self.enabled:
            c.execute("""SELECT * FROM coloring_pics""")
            for cp in c.fetchall():
                print(cp)
                try:
                    artist = fanart_models.User.objects.get(artist_id_orig=cp['artistid'])
                    print(artist)
                    base = Base.objects.get(id_orig=cp['basepic'])
                    print(base)
                    f = ColoringPicture.objects.create(
                        id_orig = cp['coloring_picid'],
                        id = cp['coloring_picid'],
                        artist = artist,
                        base = base,
#                        date_posted = cp['posted'],
                        comment = cp['comment'],
                        filename = cp['filename'] if cp['filename'] else '',
                        picture = 'Artwork/coloring/{0}.{1}'.format(cp['coloring_picid'], cp['extension']),
#                        extension = cp['extension'],
                        width = cp['width'],
                        height = cp['height'],
#                        thumb_height = cp['thumbheight'],
                    )
                    f.date_posted = cp['posted']
                    f.save()
                except fanart_models.User.DoesNotExist:
                    print('Artist not found')
                    pass
                except Base.DoesNotExist:
                    print('Base not found')
                    pass

        if 'do_characters' in self.enabled:
#            c.execute("""SELECT * FROM characters""")
            c.execute("""SELECT * FROM characters where artistid=955""")
            for ch in c.fetchall():
                print(ch)

                creator = None
                if ch['creator']:
                    try:
                        creator = fanart_models.User.objects.get(artist_id_orig=ch['creator'])
                    except fanart_models.User.DoesNotExist:
                        creator = None
                owner = None
                if ch['artistid']:
                    try:
                        owner = fanart_models.User.objects.get(artist_id_orig=ch['artistid'])
                    except fanart_models.User.DoesNotExist:
                        owner = None
                adopted_from = None
                if ch['adoptedfrom']:
                    try:
                        adopted_from = fanart_models.User.objects.get(artist_id_orig=ch['adoptedfrom'])
                    except fanart_models.User.DoesNotExist:
                        adopted_from = None
                try:
                    profile_picture = fanart_models.Picture.objects.get(id_orig=ch['profilepic'])
                except fanart_models.Picture.DoesNotExist:
                    profile_picture = None
                try:
                    profile_coloring_picture = ColoringPicture.objects.get(id_orig=ch['profilepic_c'])
                except ColoringPicture.DoesNotExist:
                    profile_coloring_picture = None
                f = fanart_models.Character.objects.create(
                    id_orig = ch['characterid'],
                    id = ch['characterid'],
                    creator = creator,
                    owner = owner,
                    is_canon = True if ch['artistid'] == None else False,
                    adopted_from = adopted_from,
                    name = ch['charactername'],
                    description = ch['description'],
                    species = ch['species'] if ch['species'] else '',
                    sex = self.GENDERS[ch['sex']],
                    story_title = ch['storyname'] if ch['storyname'] else '',
                    story_url = ch['storyurl'] if ch['storyurl'] else '',
                    date_modified = ch['lastmod'],
                    date_adopted = ch['adopted'],
                    date_deleted = ch['deleted'],
                    profile_picture = profile_picture,
                    profile_coloring_picture = profile_coloring_picture,
                )
                f.date_created = ch['created']
                f.save()
#                f.id = f.id_orig
#                f.save()

        if 'do_favorites' in self.enabled:
            c.execute("""SELECT * FROM favorites""")
            for fave in c.fetchall():
                print(fave)
                try:
                    user = fanart_models.User.objects.get(id_orig=fave['userid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                    print('User not found')
                try:
                    artist = fanart_models.User.objects.get(artist_id_orig=fave['artistid'])
                except fanart_models.User.DoesNotExist:
                    artist = None
                    print('Artist not found')
                f = fanart_models.Favorite.objects.create(
                    user = user,
                    artist = artist,
#                    date_added = fave['added'],
                    is_visible = fave['visible'] if fave['visible'] != None else True,
                    last_viewed = fave['lastviewed'],
                )
                f.date_added = fave['added']
                f.save()

            c.execute("""SELECT * FROM favepics""")
            for fave in c.fetchall():
                print(fave)
                try:
                    user = fanart_models.User.objects.get(id_orig=fave['userid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                try:
                    picture = fanart_models.Picture.objects.get(id_orig=fave['pictureid'])
                except fanart_models.Picture.DoesNotExist:
                    picture = None
                f = fanart_models.Favorite.objects.create(
                    user = user,
                    picture = picture,
#                    date_added = fave['added'],
                )
                f.date_added = fave['added']
                f.save()

        if 'do_offers' in self.enabled:
            c.execute("""SELECT * FROM offers""")
            for offer in c.fetchall():
                print(offer)
                try:
                    artist = fanart_models.User.objects.get(artist_id_orig=offer['artistid'])
                except fanart_models.User.DoesNotExist:
                    artist = None
                try:
                    character = fanart_models.Character.objects.get(id_orig=offer['characterid'])
                except fanart_models.Character.DoesNotExist:
                    character = None
                adopted_by = None
                if offer['adoptedby']:
                    try:
                        adopted_by = fanart_models.User.objects.get(artist_id_orig=offer['adoptedby'])
                    except fanart_models.User.DoesNotExist:
                        adopted_by = None
                f = Offer.objects.create(
                    id_orig = offer['offerid'],
                    id = offer['offerid'],
                    artist = artist,
                    type = offer['type'],
#                    date_posted = offer['posted'],
                    title = offer['title'],
                    comment = offer['comment'],
                    filename = offer['filename'] if offer['filename'] else '',
#                    basename = offer['basename'] if offer['basename'] else '',
#                    extension = offer['extension'] if offer['extension'] else '',
#                    thumb_height = offer['thumbheight'],
                    character = character,
                    adopted_by = adopted_by,
                    is_active = offer['active'],
                    is_visible = offer['visible'],
                )
                f.date_posted = offer['posted']
                f.save()

        if 'do_claims' in self.enabled:
            c.execute("""SELECT * FROM claims""")
            for claim in c.fetchall():
                print(claim)
                try:
                    offer = Offer.objects.get(id_orig=claim['offerid'])
                except Offer.DoesNotExist:
                    offer = None
                try:
                    user = fanart_models.User.objects.get(id_orig=claim['userid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                f = Claim.objects.create(
                    id_orig = claim['claimid'],
                    id = claim['claimid'],
                    offer = offer,
                    user = user,
                    date_posted = claim['posted'],
                    comment = claim['comment'] if claim['comment'] else '',
                    reference_url = claim['refurl'] if claim['refurl'] else '',
                    date_fulfilled = claim['fulfilled'],
                    filename = claim['filename'] if claim['filename'] else '',
#                    basename = claim['basename'] if claim['basename'] else '',
#                    extension = claim['extension'] if claim['extension'] else '',
                    date_uploaded = claim['picdate'],
                )
                f.date_posted = claim['posted']
                f.save()

        if 'do_picturecharacters' in self.enabled:
            c.execute("""SELECT * FROM picturecharacters""")
            for pc in c.fetchall():
                print(pc)
                try:
                    character = fanart_models.Character.objects.get(id_orig=pc['characterid'])
                except fanart_models.Character.DoesNotExist:
                    character = None
                try:
                    picture = fanart_models.Picture.objects.get(id_orig=pc['pictureid'])
                except fanart_models.Picture.DoesNotExist:
                    picture = None
                    print('Picture {0} not found'.format(pc['pictureid']))
                try:
                    pending = fanart_models.Pending.objects.get(id=pc['pendingid'])
                except fanart_models.Pending.DoesNotExist:
                    pending = None
                f = fanart_models.PictureCharacter.objects.create(
                    picture = picture,
                    pending = pending,
                    character = character,
                )
                f.date_tagged = pc['tagged_on']
                f.save()
                character.num_pictures = character.picturecharacter_set.count()
                character.save()
                if f.date_tagged and (character.date_tagged == None or f.date_tagged.replace(tzinfo=timezone.utc) > character.date_tagged):
                    character.date_tagged = f.date_tagged
                    character.save()

        if 'do_tags' in self.enabled:
            c.execute("""SELECT * FROM tags""")
            for tag in c.fetchall():
                print(tag)
                f = fanart_models.Tag.objects.create(
                    id_orig = tag['tagid'],
                    id = tag['tagid'],
                    tag = tag['tag'],
#                    num_pictures = tag['numpictures'],
                    is_visible = tag['visible'],
                )
            c.execute("""SELECT * FROM picturetags""")
            for pt in c.fetchall():
                print(pt)
                try:
                    picture = fanart_models.Picture.objects.get(id_orig=pt['pictureid'])
                    tag = fanart_models.Tag.objects.get(id_orig=pt['tagid'])
                    picture.tags.add(tag)
                except fanart_models.Picture.DoesNotExist:
                    pass
                except fanart_models.Tag.DoesNotExist:
                    pass

        if 'do_approvers' in self.enabled:
            c.execute("""SELECT * FROM approvers""")
            for a in c.fetchall():
                print(a)
                u = fanart_models.User.objects.get(id_orig=a['userid'])
                u.is_approver = True
                u.save()

        if 'do_sketcheradmins' in self.enabled:
            c.execute("""SELECT * FROM sketcheradmins""")
            for a in c.fetchall():
                print(a)
                try:
                    u = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                    u.is_sketcher_mod = True
                    u.save()
                except fanart_models.User.DoesNotExist:
                    pass

        if 'do_requests' in self.enabled:
#            c.execute("""SELECT * FROM requests""")
            c.execute("""SELECT * FROM requests where recptid=955""")
            for a in c.fetchall():
                print(a)
                try:
                    artist = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    artist = None
                try:
                    recipient = fanart_models.User.objects.get(artist_id_orig=a['recptid'])
                except fanart_models.User.DoesNotExist:
                    recipient = None
                try:
                    picture = fanart_models.Picture.objects.get(id_orig=a['pictureid'])
                except fanart_models.Picture.DoesNotExist:
                    picture = None
                f = fanart_models.GiftPicture.objects.create(
                    id = a['requestid'],
                    sender = artist,
                    recipient = recipient,
                    picture = picture,
                    filename = a['filename'] if a['filename'] else '',
                    message = a['sendmsg'],
                    is_active = a['active'],
#                    date_sent = a['sent'],
                    date_accepted = a['accepted'],
                    hash = a['hash'][1:] if a['hash'] else None,
                )
                f.date_sent = a['sent']
                f.save()

        if 'do_imclients' in self.enabled:
            c.execute("""SELECT * FROM imclients""")
            for a in c.fetchall():
                print(a)
                f = fanart_models.SocialMedia.objects.create(
                    id_orig = a['imclientid'],
                    id = a['imclientid'],
                    name = a['imclient'],
                )

        if 'do_imids' in self.enabled:
            c.execute("""SELECT * FROM imids""")
            for a in c.fetchall():
                print(a)
                try:
                    user = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                try:
                    social_media = fanart_models.SocialMedia.objects.get(id_orig=a['imclientid'])
                except fanart_models.SocialMedia.DoesNotExist:
                    social_media = None
                f = fanart_models.SocialMediaIdentity.objects.create(
                    user = user,
                    social_media = social_media,
                    identity = a['imid'],
                )

        if 'do_newpics' in self.enabled:
            c.execute("""SELECT * FROM newpics""")
            for a in c.fetchall():
                try:
                    user = fanart_models.User.objects.get(id_orig=a['userid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                try:
                    picture = fanart_models.Picture.objects.get(id_orig=a['pictureid'])
                except fanart_models.Picture.DoesNotExist:
                    picture = None
                f = fanart_models.UnviewedPicture.objects.create(
                    user = user,
                    picture = picture,
                )
                f.date_added = a['added']
                f.save()

        if 'do_approval_access' in self.enabled:
            c.execute("""SELECT * FROM approval_access""")
            for a in c.fetchall():
                try:
                    user = fanart_models.User.objects.get(id_orig=a['userid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                f = fanart_models.ApprovalAccess.objects.create(
                    user = user,
                    login = a['login'],
                    logout = a['logout'],
                )

        if 'do_adminblog' in self.enabled:
            c.execute("""SELECT * FROM adminblog""")
            for a in c.fetchall():
                try:
                    user = fanart_models.User.objects.get(artist_id_orig=a['adminid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                f = fanart_models.AdminBlog.objects.create(
                    user = user,
                    message = a['message'],
                )
                f.date_posted = a['posted']
                f.save()

        if 'do_artistnames' in self.enabled:
            c.execute("""SELECT * FROM artistnames""")
            for a in c.fetchall():
                try:
                    artist = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    artist = None
                f = fanart_models.ArtistName.objects.create(
                    artist = artist,
                    name = a['name'],
                )
                f.date_changed = a['changedon']
                f.save()

        if 'do_blocks' in self.enabled:
            c.execute("""SELECT * FROM blocks""")
            for a in c.fetchall():
                try:
                    user = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                try:
                    blocked_user = fanart_models.User.objects.get(id_orig=a['userid'])
                except fanart_models.User.DoesNotExist:
                    blocked_user = None
                f = fanart_models.Block.objects.create(
                    user = user,
                    blocked_user = blocked_user,
                )
                f.date_blocked = a['blockedon']
                f.save()

        if 'do_bulletins' in self.enabled:
            c.execute("""SELECT * FROM bulletins""")
            for a in c.fetchall():
                print(a)
                user = None
                if a['artistid']:
                    try:
                        user = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                    except fanart_models.User.DoesNotExist:
                        user = None
                f = fanart_models.Bulletin.objects.create(
                    user = user,
                    is_published = a['published'],
                    date_published = a['publishedon'],
                    title = a['title'],
                    bulletin = a['bulletin'],
                    is_admin = a['admin'],
                    show_email = a['showemail'] if a['showemail'] != None else False,
                )
                f.date_posted = a['posted']
                f.save()

        if 'do_contests' in self.enabled:
            c.execute("""SELECT * FROM contests""")
            for a in c.fetchall():
                print(a)
                try:
                    creator = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    creator = None
                f = fanart_models.Contest.objects.create(
                    id_orig = a['contestid'],
                    id = a['contestid'],
                    type = a['type'],
                    creator = creator,
                    title = a['title'],
                    description = a['description'],
                    rules = a['rules'],
                    date_start = a['startdate'],
                    date_end = a['deadline'],
                    is_active = a['active'],
                    is_cancelled = a['cancelled'],
                    allow_multiple_entries = a['allowmultiple'],
                    allow_anonymous_entries = a['anonymous'],
                    allow_voting = a['allowvoting'],
                )
                f.date_created = a['created']
                f.save()

        if 'do_contestpics' in self.enabled:
            c.execute("""SELECT * FROM contestpics""")
            for a in c.fetchall():
                print(a)
                try:
                    contest = fanart_models.Contest.objects.get(id_orig=a['contestid'])
                except fanart_models.Contest.DoesNotExist:
                    contest = None
                try:
                    picture = fanart_models.Picture.objects.get(id_orig=a['pictureid'])
                except fanart_models.Picture.DoesNotExist:
                    picture = None
                f = fanart_models.ContestEntry.objects.create(
                    id_orig = a['contestpicid'],
                    id = a['contestpicid'],
                    contest = contest,
                    picture = picture,
#                    date_entered = a['entered'],
                    date_notified = a['emailsent'],
                )
                print(a['entered'])
                f.date_entered = a['entered']
                f.save()
                print(f.date_entered)

        if 'do_contestvotes' in self.enabled:
            c.execute("""SELECT * FROM contestvotes""")
            for a in c.fetchall():
                print(a)
                try:
                    user = fanart_models.User.objects.get(id_orig=a['userid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                try:
                    entry = fanart_models.ContestEntry.objects.get(id_orig=a['contestpicid'])
                except fanart_models.ContestEntry.DoesNotExist:
                    entry = None
                f = fanart_models.ContestVote.objects.create(
                    user = user,
                    entry = entry,
                    date_voted = a['voted'],
                )

        if 'do_pms' in self.enabled:
            self.get_child_pms(c, 0, None)

        if 'do_specials' in self.enabled:
            c.execute("""SELECT * FROM specials""")
            for a in c.fetchall():
                print(a)
                f = fanart_models.Showcase.objects.create(
                    keyword = a['keyword'],
                    title = a['title'],
                    description = a['description'],
                    is_visible = a['visible'],
                )

        if 'do_votes' in self.enabled:
            c.execute("""SELECT * FROM votes""")
            for a in c.fetchall():
                print(a)
                try:
                    voter = fanart_models.User.objects.get(id_orig=a['userid'])
                except fanart_models.User.DoesNotExist:
                    voter = None
                try:
                    artist = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    artist = None
                f = fanart_models.Vote.objects.create(
                    voter = voter,
                    artist = artist,
                )

        if 'do_customicons' in self.enabled:
            c.execute("""SELECT * FROM customicons""")
            for a in c.fetchall():
                print(a)
                try:
                    user = fanart_models.User.objects.get(artist_id_orig=a['artistid'])
                except fanart_models.User.DoesNotExist:
                    user = None
                f = fanart_models.CustomIcon.objects.create(
                    user = user,
                    icon_id = a['icon'],
                    extension = a['ext'],
                    type = a['type'],
                )
