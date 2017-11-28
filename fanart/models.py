from __future__ import unicode_literals

from django.conf import settings
from django.db import models, connection
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, UserManager, AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import uuid
import datetime
import os
import re

from fanart.utils import dictfetchall
from fanart.tasks import process_images

import logging
logger = logging.getLogger(__name__)

THREE = 90


def get_media_path(instance, filename):
    return '{0}/{1}'.format(instance.id, filename)

def get_claims_path(instance, filename):
    return 'Artwork/claims/{0}.{1}'.format(instance.id, instance.extension)

def get_claims_thumb_path(instance, filename):
    return 'Artwork/claims/{0}.s.jpg'.format(instance.id)

def get_coloring_path(instance, filename):
    return 'Artwork/coloring/{0}.{1}'.format(instance.id, instance.extension)

def get_coloring_thumb_path(instance, filename):
    return 'Artwork/coloring/{0}.s.jpg'.format(instance.id)

def get_profile_path(instance, filename):
    extension = filename.split('.')[-1].lower()
    filename = '{0}.{1}'.format(uuid.uuid4(), extension)
    return 'profiles/{0}'.format(filename)

def get_pending_path(instance, filename):
    return 'pending/{0}/{1}'.format(uuid.uuid4(), filename)

#def get_image_thumb_small_path(instance, filename):
#    return '{0}/thumb_small/{1}'.format(instance.id, filename)
#
#def get_image_thumb_large_path(instance, filename):
#    return '{0}/thumb_large/{1}'.format(instance.id, filename)


def validate_unique_username(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError(
            _('The name %(value)s is already in use.'),
            params={'value': value},
        )

def validate_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            _('The email %(value)s is already in use.'),
            params={'value': value},
        )


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class FanartUserManager(UserManager):

    def recently_active(self):
        return self.get_queryset().filter(is_artist=True, is_active=True, is_public=True, num_pictures__gt=0).order_by('-last_upload')[0:10]


class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('neither', '(No response)'),
    )

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
#        validators=[username_validator],
        validators=[validate_unique_username],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    last_host = models.CharField(max_length=128, null=True, blank=True)
    h_size = models.IntegerField(null=True, blank=True)
    v_size = models.IntegerField(null=True, blank=True)
    show_favorite_artists_box = models.BooleanField(default=True)
    show_favorite_pictures_box = models.BooleanField(default=True)
    show_sketcher_box = models.BooleanField(default=True)
    show_community_art_box = models.BooleanField(default=True)
    show_contests_box = models.BooleanField(default=True)
    show_tool_box = models.BooleanField(default=True)
    folders_tree = models.BooleanField(default=False)

    artist_id_orig = models.IntegerField(null=True, blank=True, db_index=True)

    dir_name = models.CharField(max_length=150, blank=True, db_index=True)
    sort_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True, help_text='Controls whether user is allowed to log in. Uncheck this to disable accounts.')
    is_artist = models.BooleanField(default=True, help_text='Controls whether user has a visible artist page and has access to artist modules in ArtManager, or simply a Profile for following others.')
    is_public = models.BooleanField(default=True, help_text='Controls whether user\'s art page is publicly visible to unauthenticated users')
    is_paid = models.BooleanField(default=True)
    num_pictures = models.IntegerField(default=0)
    num_faves = models.IntegerField(default=0)
    num_favepics = models.IntegerField(default=0)
    num_characters = models.IntegerField(default=0)
    last_upload = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    birthday = models.CharField(max_length=30, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=255, blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    featured = models.CharField(max_length=7, null=True, blank=True)
    comments = models.TextField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    banner_text = models.TextField(blank=True)
    banner_text_updated = models.DateTimeField(null=True, blank=True)
    banner_text_min = models.TextField(blank=True)
    zip_enabled = models.BooleanField(default=True)
    show_email = models.BooleanField(default=True)
    show_birthdate = models.BooleanField(default=True)
    show_birthdate_age = models.BooleanField(default=True)
    allow_shouts = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    email_shouts = models.BooleanField(default=True)
    email_comments = models.BooleanField(default=True)
    email_pms = models.BooleanField(default=True)
    show_coloring_cave = models.BooleanField(default=True)
    commissions_open = models.BooleanField(default=True)

    profile_picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='profile_height', width_field='profile_width', upload_to=get_profile_path, null=True, blank=True)
    profile_width = models.IntegerField(null=True, blank=True)
    profile_height = models.IntegerField(null=True, blank=True)

    profile_pic_id = models.IntegerField(null=True, blank=True)
    profile_pic_ext = models.CharField(max_length=5, blank=True)
    banner_id = models.IntegerField(null=True, blank=True)
    banner_ext = models.CharField(max_length=5, blank=True)
    example_pic = models.ForeignKey('Picture', null=True, blank=True)
    suspension_message = models.TextField(blank=True)
    auto_approve = models.BooleanField(default=False)
    allow_sketcher = models.BooleanField(default=True)
    sketcher_banned = models.DateTimeField(null=True, blank=True)
    sketcher_banned_by = models.ForeignKey('User', null=True, blank=True)
    sketcher_ban_reason = models.TextField(blank=True)
    is_approver = models.BooleanField(default=False)
    is_sketcher_mod = models.BooleanField(default=False)

    objects = FanartUserManager()

    def get_absolute_url(self):
        return '{0}/Artists/{1}/'.format(settings.SERVER_BASE_URL, self.dir_name)

    @property
    def show_guidelines(self):
        return self.num_pictures < settings.MIN_PICTURES_TO_HIDE_GUIDELINES

    @property
    def get_example_pic(self):
        if self.example_pic:
            return self.example.pic
        return self.picture_set.filter(date_deleted__isnull=True, is_public=True).order_by('?').first()

    @property
    def unread_received_pms_count(self):
        return self.pms_received.filter(date_viewed__isnull=True).count()

    @property
    def favorite_artists(self):
#        return self.favorite_set.filter(artist__isnull=False, picture__isnull=True).order_by('artist__sort_name')

        with connection.cursor() as cursor:
            query = """
SELECT fanart_favorite.artist_id,fanart_user.username,fanart_user.dir_name,fanart_favorite.is_visible,fanart_user.commissions_open,count(distinct fanart_unviewedpicture.picture_id) AS new
FROM fanart_user,fanart_favorite
LEFT JOIN fanart_unviewedpicture ON fanart_unviewedpicture.artist_id=fanart_favorite.artist_id AND fanart_unviewedpicture.user_id=fanart_favorite.user_id
WHERE fanart_user.id=fanart_favorite.artist_id
AND fanart_favorite.user_id=%s
AND fanart_favorite.picture_id IS NULL
AND fanart_favorite.character_id IS NULL
AND fanart_user.is_active=true
AND fanart_user.is_artist=true
GROUP BY fanart_favorite.artist_id
ORDER BY fanart_user.sort_name
"""
            cursor.execute(query, [self.id])
            result = dictfetchall(cursor)
        return result

    @property
    def favorite_pictures(self):
        return self.favorite_set.filter(artist__isnull=True, picture__isnull=False, character__isnull=True, picture__date_deleted__isnull=True).prefetch_related('picture').order_by('-date_added')

    @property
    def recently_uploaded_pictures(self):
        three_days_ago = timezone.now() - datetime.timedelta(days=THREE)
        return self.picture_set.filter(is_public=True, date_deleted__isnull=True, date_uploaded__gt=three_days_ago).order_by('-date_uploaded')[0:10]

    @property
    def blocked_commenters(self):
        return [b.blocked_user for b in self.blocked_by.all()]

    @property
    def unread_comments(self):
        return PictureComment.objects.filter(picture__artist=self, is_received=False).order_by('-date_posted')

    @property
    def unread_shouts(self):
        return Shout.objects.filter(artist=self, is_received=False).order_by('-date_posted')

    @property
    def first_upload(self):
        try:
            return self.picture_set.all().order_by('date_uploaded').first().date_uploaded
        except AttributeError:
            return None

    @property
    def open_gifts_received(self):
        return self.gifts_received.filter(is_active=False)

    @property
    def icon_claims_ready(self):
        return TradingClaim.objects.filter(offer__type='icon', user=self, offer__is_visible=True, date_fulfilled__isnull=True).exclude(filename='').order_by('-date_posted')

    @property
    def adoptable_claims_ready(self):
        return TradingClaim.objects.filter(offer__type='adoptable', user=self, offer__is_visible=True, date_fulfilled__isnull=False).order_by('-date_posted')

    @property
    def claims_ready(self):
        return self.icon_claims_ready.union(self.adoptable_claims_ready)

    @property
    def banner_url(self):
        return '{0}Artwork/banners/{1}.{2}'.format(settings.MEDIA_URL, self.banner_id, self.banner_ext)

    @property
    def profile_pic_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '{0}profiles/{1}.{2}'.format(settings.MEDIA_URL, self.profile_pic_id, self.profile_pic_ext)

    @property
    def profile_pic_thumbnail_url(self):
#        return '{0}profiles/{1}'.format(settings.MEDIA_URL, self.profile_pic_thumbnail)

        if self.profile_picture and self.profile_pic_thumbnail_created:
            return '{0}profiles/{1}'.format(settings.MEDIA_URL, self.profile_pic_thumbnail)
        elif self.profile_pic_id:
            return '{0}profiles/{1}.s.{2}'.format(settings.MEDIA_URL, self.profile_pic_id, self.profile_pic_ext)
        return '{0}images/loading2.gif'.format(settings.STATIC_URL)

    @property
    def profile_pic_thumbnail_created(self):
        return os.path.exists(self.profile_pic_thumbnail_path)

    @property
    def profile_pic_thumbnail_path(self):
        path_parts = self.profile_picture.name.split('/')
        path = '/'.join(path_parts[:-1])
        filename_parts = path_parts[-1].split('.')
        basename = '.'.join(filename_parts[:-1])
        extension = filename_parts[-1].lower()
        return '{0}/{1}/{2}.s.{3}'.format(settings.MEDIA_ROOT, path, basename, extension)

    @property
    def profile_pic_thumbnail(self):
        if self.profile_picture:
            filename_parts = (self.profile_picture.path.split('/')[-1]).split('.')
            basename = '.'.join(filename_parts[:-1])
            extension = filename_parts[-1].lower()
            return '{0}.s.{1}'.format(basename, extension)

#            path = ('/').join(self.picture.path.split('/')[:-1])
#            return '{0}/{1}.s.jpg'.format(path, self.id)

        return '{0}.s.{1}'.format(self.profile_pic_id, self.profile_pic_ext)

    @property
    def birthdate_age(self):
        if not self.birth_date:
            return None
        now = timezone.now()
        years = now.year - self.birth_date.year
        if now.month < self.birth_date.month or (now.month == self.birth_date.month and now.day < self.birth_date.day):
            years -= 1
        return years

    @property
    def past_names(self):
        return self.artistname_set.order_by('-date_changed')

    @property
    def username_escaped(self):
        return self.username.replace('"', '\\\"')

    @property
    def sort_name_escaped(self):
        return self.sort_name.replace('"', '\\\"')

    @property
    def absolute_dir_name(self):
        return '{0}/Artwork/Artists/{1}'.format(settings.MEDIA_ROOT, self.dir_name)

    def change_dir_name(self):
        new_dir_name = re.sub('&#[0-9]+;', 'x', self.username)
        new_dir_name = re.sub("[\\']", '', new_dir_name)
        new_dir_name = re.sub('[^a-zA-Z0-9]', '_', new_dir_name)

        if new_dir_name == self.dir_name:
            return self.dir_name

        new_absolute_dir_name = '{0}/Artwork/Artists/{1}'.format(settings.MEDIA_ROOT, new_dir_name)

        if os.path.isdir(new_absolute_dir_name):
            raise ValidationError(
                _('The directory name %(value)s is already in use.'),
                params={'value': new_dir_name},
            )

        os.rename(self.absolute_dir_name, new_absolute_dir_name)
        self.dir_name = new_dir_name
        self.save()

        return new_dir_name

    def refresh_num_pictures(self):
        self.num_pictures = self.picture_set.count()
        self.save()

    def refresh_picture_ranks(self, folder=None, refresh_folder=False):
        pictures = self.picture_set.order_by('date_uploaded')
        if refresh_folder:
            pictures = pictures.filter(folder=folder)
        for i, picture in enumerate(pictures):
            if refresh_folder:
                picture.rank_in_folder = i + 1
            else:
                picture.rank_in_artist = i + 1
            picture.save()

    def save(self, update_thumbs=False, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(User, self).save(*args, **kwargs)
        logger.info(self.profile_picture)
        if update_thumbs:
            process_images.apply_async(('User', self.id, 'small'), countdown=20)
            if self.profile_width > settings.THUMB_SIZE['profile'] or self.profile_height > settings.THUMB_SIZE['profile']:
                process_images.apply_async(('User', self.id, 'profile'), countdown=20)

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.id, self.username, self.email)


class PictureManager(models.Manager):

    def get_queryset(self):
        return super(PictureManager, self).get_queryset().exclude(date_deleted__isnull=False)


class Picture(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('User', null=True)
    folder = models.ForeignKey('Folder', null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    extension = models.CharField(max_length=5, blank=True)
    title = models.TextField(blank=True)
    is_color = models.BooleanField(default=True)
    type = models.CharField(max_length=32, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.IntegerField(blank=True)
    quality = models.CharField(max_length=1, blank=True)
    thumb_height = models.IntegerField(blank=True)
    num_comments = models.IntegerField(default=0)
    num_faves = models.IntegerField(default=0)
#    characters = models.CharField(max_length=50, blank=True)
    width = models.IntegerField(blank=True)
    height = models.IntegerField(blank=True)
    date_uploaded = models.DateTimeField(null=True, blank=True, db_index=True)
    date_approved = models.DateTimeField(null=True, blank=True, db_index=True)
    date_updated = models.DateTimeField(null=True, blank=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    hash = models.CharField(max_length=32, blank=True)
    is_public = models.BooleanField(default=True)
    rank_in_artist = models.IntegerField(default=0)
    rank_in_folder = models.IntegerField(default=0)
    approved_by = models.ForeignKey('User', null=True, blank=True, related_name='inserted')
    keywords = models.TextField(blank=True)
    work_in_progress = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    is_scanned = models.BooleanField(default=False)
    watchers_notified = models.BooleanField(default=False)
    needs_poster = models.BooleanField(default=False)
    characters = models.ManyToManyField('Character', through='PictureCharacter')
    tags = models.ManyToManyField('Tag', blank=True)

    objects = PictureManager()

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def thumbnail_url(self):
        return '{0}Artwork/Artists/{1}/{2}.s.jpg'.format(settings.MEDIA_URL, self.artist.dir_name, self.basename)

    @property
    def preview_url(self):
        return '{0}Artwork/Artists/{1}/{2}.p.jpg'.format(settings.MEDIA_URL, self.artist.dir_name, self.basename)

    @property
    def url(self):
        return '{0}Artwork/Artists/{1}/{2}'.format(settings.MEDIA_URL, self.artist.dir_name, self.filename)

    @property
    def preview_extension(self):
        if self.mime_type in ['image/jpeg', 'image/png', 'image/gif']:
            return self.extension
        return 'p.jpg'

    @property
    def preview_width(self):
        return settings.THUMB_SIZE['large']

    @property
    def preview_height(self):
        return int(self.height * settings.THUMB_SIZE['large'] / self.width)

    @property
    def thumb_height_x2(self):
        return self.thumb_height * 2

    @property
    def adjacent_pictures_in_artist(self):
        return self.artist.picture_set.filter(rank_in_artist__gte=self.rank_in_artist - 1, rank_in_artist__lte=self.rank_in_artist + 1, is_public=True).exclude(pk=self.id).order_by('rank_in_artist')

    @property
    def adjacent_pictures_in_folder(self):
        return self.artist.picture_set.filter(rank_in_folder__gte=self.rank_in_folder - 1, rank_in_folder__lte=self.rank_in_folder + 1, is_public=True, folder=self.folder).exclude(pk=self.id).order_by('rank_in_folder')

    @property
    def previous_picture_in_artist(self):
        if self.adjacent_pictures_in_artist.count() == 0:
            return None
        if self.adjacent_pictures_in_artist[0].rank_in_artist > self.rank_in_artist:
            return None
        return self.adjacent_pictures_in_artist[0]

    @property
    def next_picture_in_artist(self):
        if self.adjacent_pictures_in_artist.count() < 2:
            return None
        return self.adjacent_pictures_in_artist[1]

    @property
    def previous_picture_in_folder(self):
        if self.adjacent_pictures_in_folder.count() == 0:
            return None
        if self.adjacent_pictures_in_folder[0].rank_in_folder > self.rank_in_folder:
            return None
        return self.adjacent_pictures_in_folder[0]

    @property
    def next_picture_in_folder(self):
        if self.adjacent_pictures_in_folder.count() < 2:
            return None
        return self.adjacent_pictures_in_folder[1]

    @property
    def pictures_in_folder(self):
        if self.folder == None:
            return Picture.objects.filter(user=self.artist, folder=None)
        return self.folder.picture_set

    @property
    def tagged_characters(self):
        return [pc.character for pc in self.picturecharacter_set.all()]

    @property
    def keywords_string(self):
        return ','.join([t.tag for t in self.tags.all()])

    @property
    def character_id_list(self):
        return ','.join([str(pc.character.id) for pc in self.picturecharacter_set.all()])

    @property
    def replacement_pending(self):
        return Pending.objects.filter(replaces_picture=self).exists()

    def get_absolute_url(self):
        return reverse('artmanager:artwork-picture-detail', kwargs={'picture_id': self.id})

    def set_deleted(self):

        UnviewedPicture.objects.filter(picture=self).delete()

#                        <sql:update var="updNewPics">
#                        DELETE FROM newpics
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#                        <sql:update var="updNewPicsPending">
#                        DELETE FROM newpics_pending
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#        Favorite.objects.filter(picture=self).delete()

#                        <sql:update var="updFavePics">
#                        DELETE FROM favepics
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#        for comment in PictureComment.objects.filter(picture=self):
#            comment.is_deleted = True
#            comment.save()

#                        <sql:update var="updComments">
#                        UPDATE comments
#                        SET deleted=1
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#                        <sql:update var="updContestVotes">
#                        DELETE FROM contestvotes
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#                        <sql:update var="updContestPics">
#                        DELETE FROM contestpics
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#                        <sql:update var="updCCPic">
#                        UPDATE coloring_base
#                        SET active=false
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

        for character in Character.objects.filter(profile_picture=self):
            character.profile_picture = None
            character.save()

#                        <sql:update var="updCharacters">
#                        UPDATE characters
#                        SET profilepic=0
#                        WHERE profilepic=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

        if self.artist.example_pic == self:
            self.artist.example_pic = None
            self.artist.save()

#                        <sql:update var="updArtist">
#                        UPDATE artists
#                        SET examplepic=0
#                        WHERE examplepic=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

#                        <sql:query var="qryRequests">
#                        SELECT * FROM requests,artists
#                        WHERE requests.recptid=artists.artistid
#                        AND pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:query>

#                        <c:forEach var="request" items="${qryRequests.rows}">
#
#                                Removing request for ${request.artistname}...<br />
#
#                                <sql:update var="updRequest">
#                                DELETE FROM requests
#                                WHERE requestid=?
#                                <sql:param value="${request.requestid}" />
#                                </sql:update>
#
#                        </c:forEach>

#                        <sql:query var="qryPictureTags">
#                        SELECT * FROM picturetags
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:query>

#                        <c:forEach var="tag" items="${qryPictureTags.rows}">
#
#                                <sql:update var="updTag">
#                                UPDATE tags
#                                SET numpictures=numpictures-1
#                                WHERE tagid=?
#                                <sql:param value="${tag.tagid}" />
#                                </sql:update>
#
#                        </c:forEach>

#                        <%-- Clear tagged characters --%>
#                        <sql:update var="updPictureCharacters">
#                        DELETE FROM picturecharacters
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

        self.date_deleted = timezone.now()
        self.save()

#                        <%-- Delete the picture --%>
#                        <sql:update var="updPicture">
#                        UPDATE pictures
#                        SET deleted=NOW()
#                        WHERE pictureid=?
#                        <sql:param value="${pic}" />
#                        </sql:update>

        self.artist.refresh_num_pictures()
        self.artist.refresh_picture_ranks()
        self.artist.refresh_picture_ranks(refresh_folder=True, folder=self.folder)

#                        <%-- Update picture count for the artist --%>
#                        <sql:query var="qryNumPicsArtist">
#                        SELECT * FROM pictures
#                        WHERE artistid=?
#                        AND deleted IS NULL
#                        <sql:param value="${artist.artistid}" />
#                        </sql:query>
#                        <sql:update var="updNumPicsArtist">
#                        UPDATE artists SET numpictures=?
#                        WHERE artistid=?
#                        <sql:param value="${qryNumPicsArtist.rowCount}" />
#                        <sql:param value="${artist.artistid}" />
#                        </sql:update>

        if self.folder:
            self.folder.refresh_num_pictures()


#                        <%-- Update picture count for this folder --%>
#                        <c:if test="${picture.folderid > 0}">
#                                <sql:query var="qryNumPicsFolder">
#                                SELECT * FROM pictures
#                                WHERE folderid=?
#                                AND deleted IS NULL
#                                <sql:param value="${picture.folderid}" />
#                                </sql:query>
#                                <sql:update var="updNumPicsFolder">
#                                UPDATE folders SET numpictures=?
#                                WHERE folderid=?
#                                <sql:param value="${qryNumPicsFolder.rowCount}" />
#                                <sql:param value="${picture.folderid}" />
#                                </sql:update>
#                        </c:if>

        logger.info('Picture {0} by {1} was deleted.'.format(self, self.artist))

#                        <c:set var="artistid" value="${artist.artistid}" />
#                        <c:set var="pictureid" value="${pic}" />
#                        <c:set var="dirname" value="${artist.dirname}" />
#                        <c:set var="basename" value="${picture.basename}" />
#                        <c:set var="extension" value="${picture.extension}" />
#                        <%
#                          String artistid = (String)pageContext.getAttribute("artistid").toString();
#                          String pictureid = (String)pageContext.getAttribute("pic").toString();
#                          String basepath = (String)pageContext.getAttribute("basepath");
#                          String dirname = (String)pageContext.getAttribute("dirname");
#                          String basename = (String)pageContext.getAttribute("basename");
#                          String extension = (String)pageContext.getAttribute("extension");
#
#                          File f = new File(basepath + "/Artwork/Artists/" + dirname + "/" + basename + "." +extension);
#                          File ft = new File(basepath + "/Artwork/Artists/" + dirname + "/" + basename + ".s.jpg");
#                          File fp = new File(basepath + "/Artwork/Artists/" + dirname + "/" + basename + ".p.jpg");
#
#                          f.delete();
#                          ft.delete();
#                          fp.delete();
#
#                          printLog("Artist " + artistid + " deleted picture " + basename + "." + extension + " (ID " + pictureid + ").");
#                        %>
#
#                        <c:set var="thisfolder" value="${picture.folderid}" />
#
#                </c:forEach>

#        </c:if>

#        </c:forEach>

#        <sql:query var="qryFolderPics">
#        SELECT pictureid FROM pictures
#        WHERE artistid=?
#        AND folderid=?
#        AND deleted IS NULL
#        ORDER BY uploaded
#        <sql:param value="${artist.artistid}" />
#        <sql:param value="${thisfolder}" />
#        </sql:query>
#        <c:set var="i" value="0" />
#        <c:forEach var="picture" items="${qryFolderPics.rows}">
#                <c:set var="i" value="${i+1}" />
#                <sql:update var="updFolderPic">
#                UPDATE pictures SET
#                rankinfolder=?
#                WHERE pictureid=?
#                <sql:param value="${i}" />
#                <sql:param value="${picture.pictureid}" />
#                </sql:update>
#        </c:forEach>

#        <sql:query var="qryArtistPics">
#        SELECT pictureid FROM pictures
#        WHERE artistid=?
#        AND deleted IS NULL
#        ORDER BY uploaded
#        <sql:param value="${artist.artistid}" />
#        </sql:query>
#        <c:set var="i" value="0" />
#        <c:forEach var="picture" items="${qryArtistPics.rows}">
#                <c:set var="i" value="${i+1}" />
#                <sql:update var="updArtistPic">
#                UPDATE pictures SET
#                rankinartist=?
#                WHERE pictureid=?
#                <sql:param value="${i}" />
#                <sql:param value="${picture.pictureid}" />
#                </sql:update>
#        </c:forEach>

    def __unicode__(self):
        return '{0} {1}'.format(self.id, self.filename)


class Folder(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey('User', null=True, blank=True)
    name = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('Folder', null=True, blank=True)
#    parent_folder_id = models.IntegerField(null=True, blank=True)
    num_pictures = models.IntegerField(default=0)
    latest_picture = models.ForeignKey('Picture', null=True, blank=True, related_name='latest_folder')
    latest_picture_date = models.DateTimeField(null=True, blank=True)

    @property
    def latest_picture(self):
        return self.picture_set.order_by('-date_uploaded').first()

    def refresh_num_pictures(self):
        logger.info('Refreshing {0}'.format(self))
        self.num_pictures = self.picture_set.count()
        self.save()

    def __unicode__(self):
        return '{0} {1}'.format(self.id, self.name)


class BaseComment(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey('User', null=True, blank=True)
    comment = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    hash = models.CharField(max_length=36, null=True, blank=True)

    def __unicode__(self):
        return '{0} {1}'.format(self.id, self.user.username)

    class Meta:
        abstract = True


class PictureComment(BaseComment):
    picture = models.ForeignKey('Picture')
    reply_to = models.ForeignKey('PictureComment', null=True, blank=True, related_name='replies')

    @property
    def num_replies(self):
        return self.replies.count()

    def get_absolute_url(self):
        return reverse('comments', kwargs={'picture_id': self.picture.id})

    def __unicode__(self):
        return '{0} {1} on {2} by {3}'.format(self.id, self.user.username, self.picture, self.picture.artist.username)


class Shout(BaseComment):
    artist = models.ForeignKey('User', null=True, blank=True, related_name='shouts_received')

    @property
    def quoted_comment(self):
        return '\n\n\n[quote]\n{0}\n[/quote]'.format(self.comment)

    def get_absolute_url(self):
        return reverse('shouts', kwargs={'artist_id': self.artist.id})

    def __unicode__(self):
        return '{0} {1} on {2}'.format(self.id, self.user.username, self.artist.username)


class Character(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('neither', 'Neither'),
    )

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    creator = models.ForeignKey('User', null=True, related_name='characters_created')
    owner = models.ForeignKey('User', null=True, blank=True)
    is_canon = models.BooleanField(default=False)
    adopted_from = models.ForeignKey('User', null=True, blank=True, related_name='characters_adopted_out')
    name = models.CharField(max_length=64, blank=True)
    profile_picture = models.ForeignKey('Picture', null=True, blank=True)
    profile_coloring_picture = models.ForeignKey('ColoringPicture', null=True, blank=True)
    description = models.TextField(blank=True)
    species = models.CharField(max_length=64, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    story_title = models.CharField(max_length=100, blank=True)
    story_url = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)
    date_modified = models.DateTimeField(null=True, blank=True)
    date_adopted = models.DateTimeField(null=True, blank=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    date_tagged = models.DateTimeField(null=True, blank=True)
    num_pictures = models.IntegerField(null=True, blank=True)

    @property
    def last_tagged(self):
        return self.picturecharacter_set.order_by('-date_tagged').first()

    @property
    def picture_url(self):
        if self.is_canon:
            for ext in ['gif', 'jpg', 'png']:
                if os.path.exists('{0}/images/canon_characters/{1}.{2}'.format(settings.MEDIA_ROOT, self.id, ext)):
                    return '{0}canon_characters/{1}.{2}'.format(settings.MEDIA_URL, self.id, ext)
            return '{0}images/blank_characterthumb.jpg'.format(settings.STATIC_URL)
        elif self.profile_picture:
            return self.profile_picture.url
        elif self.profile_coloring_picture:
            return self.profile_coloring_picture.url
        else:
            return '{0}images/blank_characterthumb.jpg'.format(settings.STATIC_URL)

    @property
    def thumbnail_url(self):
        if self.is_canon:
            return '{0}canon_characters/{1}.s.jpg'.format(settings.MEDIA_URL, self.id_orig)
        elif self.profile_picture:
            return self.profile_picture.thumbnail_url
        elif self.profile_coloring_picture:
            return self.profile_coloring_picture.thumbnail_url
        else:
            return '{0}images/blank_characterthumb.jpg'.format(settings.STATIC_URL)

    @property
    def preview_url(self):
        if self.is_canon:
            return '{0}canon_characters/{1}.p.jpg'.format(settings.MEDIA_URL, self.id_orig)
        elif self.profile_picture:
            return self.profile_picture.preview_url
        elif self.profile_coloring_picture:
            return self.profile_coloring_picture.preview_url
        else:
            return '{0}images/blank_characterthumb.jpg'.format(settings.STATIC_URL)

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.id, self.name, self.owner)


class FavoriteManager(models.Manager):

    def for_user(self, user):
        return self.get_queryset().filter(user=user, artist__isnull=False).annotate(new=models.Sum(
            models.Case(
                models.When(artist__new_pictures__user=user, then=1),
                default=0,
                output_field=models.IntegerField()
            )
        )).prefetch_related('artist').order_by('artist__sort_name')


class Favorite(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='fans')
    picture = models.ForeignKey('Picture', null=True, blank=True, related_name='fans')
    character = models.ForeignKey('Character', null=True, blank=True, related_name='fans')
    is_visible = models.BooleanField(default=True)
    date_added = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    last_viewed = models.DateTimeField(null=True, blank=True)

    objects = FavoriteManager()


class Pending(models.Model):
    artist = models.ForeignKey('User', null=True)
    folder = models.ForeignKey('Folder', null=True, blank=True)
    picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_pending_path, null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True, default='')
#    extension = models.CharField(max_length=5, blank=True, default='')
    type = models.CharField(max_length=32, blank=True)
    is_movie = models.BooleanField(default=False)
    has_thumb = models.BooleanField(default=False)
    title = models.TextField(blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    hash = models.CharField(max_length=32, blank=True)
    notify_approval = models.BooleanField(default=False)
    work_in_progress = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    replaces_picture = models.ForeignKey('Picture', null=True, blank=True)
    reset_upload_date = models.BooleanField(default=False)
    notify_replacement = models.BooleanField(default=False)
    keywords = models.TextField(blank=True)
    status = models.TextField(blank=True)
    remote_host = models.CharField(max_length=100, blank=True)
    remote_addr = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    force_approve = models.BooleanField(default=False)
    is_scanned = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('User', null=True, blank=True, related_name='approved_pictures')

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def extension(self):
        if self.filename:
            return self.filename.split('.')[-1].lower()
        return self.picture.name.split('.')[-1].lower()

    @property
    def directory(self):
        return self.picture.name.split('/')[1]

    @property
    def thumbnail_url(self):
        if os.path.exists(self.thumbnail_path):
            return '{0}pending/{1}/{2}.s.jpg'.format(settings.MEDIA_URL, self.directory, self.basename)
        return '{0}images/loading2.gif'.format(settings.STATIC_URL)

    @property
    def preview_url(self):
        return '{0}pending/{1}/{2}.p.jpg'.format(settings.MEDIA_URL, self.directory, self.basename)

    @property
    def thumbnail_path(self):
        path_parts = self.picture.name.split('/')
        path = '/'.join(path_parts[:-1])
        filename_parts = path_parts[-1].split('.')
        basename = '.'.join(filename_parts[:-1])
        extension = filename_parts[-1].lower()
        return '{0}/{1}/{2}.s.jpg'.format(settings.MEDIA_ROOT, path, basename)

    @property
    def thumbnail_created(self):
        return os.path.exists(self.thumbnail_path)

    @property
    def dimensions_warning(self):
        return self.width > settings.MAX_UPLOAD_WIDTH or self.height > settings.MAX_UPLOAD_HEIGHT

    @property
    def size_warning(self):
        return self.picture.size > settings.MAX_UPLOAD_SIZE and not self.is_movie

    @property
    def get_tags(self):
        return self.keywords.split(',')

    @property
    def tagged_characters(self):
        return [pc.character for pc in self.picturecharacter_set.all()]

    def get_absolute_url(self):
        return reverse('artmanager:pending-detail', kwargs={'pending_id': self.id})

    def save(self, update_thumbs=True, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(Pending, self).save(*args, **kwargs)
        logger.info(self.picture)
        if update_thumbs:
            process_images.apply_async(('Pending', self.id, 'small'), countdown=20)

    class Meta:
        ordering = ['date_uploaded']


class ColoringBase(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    creator = models.ForeignKey('User', null=True, blank=True)
    picture = models.ForeignKey('Picture', null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    num_colored = models.IntegerField(null=True, blank=True)

    @property
    def thumbnail_url(self):
        return '{0}Artwork/Artists/{1}/{2}.s.jpg'.format(settings.MEDIA_URL, self.picture.artist.dir_name, self.picture.basename)

    def refresh_num_colored(self):
        self.num_colored = self.coloringpicture_set.count()
        self.save()


class ColoringPicture(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('User', null=True, blank=True)
    base = models.ForeignKey('ColoringBase', null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    comment = models.TextField(blank=True)
    filename = models.CharField(max_length=100, blank=True)
    picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_coloring_path, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def extension(self):
        if self.filename:
            return self.filename.split('.')[-1].lower()
        return self.picture.name.split('.')[-1].lower()

    @property
    def thumbnail_path(self):
        if not self.picture:
            return None
        path = ('/').join(self.picture.path.split('/')[:-1])
        return '{0}/{1}.s.jpg'.format(path, self.id)

    @property
    def thumbnail_url(self):
        if os.path.exists(self.thumbnail_path):
            return '{0}Artwork/coloring/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)
        return '{0}images/loading2.gif'.format(settings.STATIC_URL)

    @property
    def thumbnail_created(self):
        return os.path.exists(self.thumbnail_path)

    @property
    def url(self):
        return '{0}Artwork/coloring/{1}.{2}'.format(settings.MEDIA_URL, self.id, self.extension)

    @property
    def preview_width(self):
        return settings.THUMB_SIZE['large']

    @property
    def preview_height(self):
        return int(self.height * settings.THUMB_SIZE['large'] / self.width)


    @property
    def thumb_width(self):
        return settings.THUMB_SIZE['small']

    @property
    def thumb_height(self):
        return int(self.height * settings.THUMB_SIZE['small'] / self.width)

    @property
    def thumb_height_x2(self):
        return self.thumb_height * 2

    def get_absolute_url(self):
        return reverse('coloring-pictures', kwargs={'coloring_base_id': self.base.id})

    def save(self, update_thumbs=True, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(ColoringPicture, self).save(*args, **kwargs)
        logger.info(self.picture)
        if update_thumbs:
            process_images.apply_async(('ColoringPicture', self.id, 'small'), countdown=20)

    def delete(self, *args, **kwargs):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.picture.name))
            os.remove(os.path.join(settings.MEDIA_ROOT, self.thumbnail_path))
        except OSError:
            pass

        for character in Character.objects.filter(profile_coloring_picture=self):
            character.profile_coloring_picture = None
            character.save()

        self.base.refresh_num_colored()

        super(ColoringPicture, self).delete(*args, **kwargs)


class TradingOffer(models.Model):
    TYPE_CHOICES = (
        ('icon', 'Icon'),
        ('adoptable', 'Adoptable'),
    )

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('User', null=True, blank=True)
    type = models.CharField(max_length=10, choices = TYPE_CHOICES, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    title = models.CharField(max_length=64, blank=True)
    comment = models.TextField(blank=True)
    filename = models.CharField(max_length=100, blank=True)
    basename = models.CharField(max_length=100, blank=True)
    extension = models.CharField(max_length=5, blank=True)
    thumb_height = models.IntegerField(blank=True)
    character = models.ForeignKey('Character', null=True, blank=True)
    adopted_by = models.ForeignKey('User', null=True, blank=True, related_name='trades_offered')
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)

    @property
    def open_claims(self):
        return self.tradingclaim_set.filter(date_fulfilled__isnull=True)

    @property
    def completed_claims(self):
        return self.tradingclaim_set.filter(date_fulfilled__isnull=False)

    @property
    def url(self):
        return '{0}Artwork/offers/{1}.{2}'.format(settings.MEDIA_URL, self.id, self.extension)

    @property
    def thumbnail_url(self):
        return '{0}Artwork/offers/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)

    def get_absolute_url(self):
        return reverse('offer', kwargs={'offer_id': self.id})


class TradingClaim(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    offer = models.ForeignKey('TradingOffer', null=True, blank=True)
    user = models.ForeignKey('User', null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    comment = models.TextField(blank=True)
    reference_url = models.CharField(max_length=255, blank=True)
    date_fulfilled = models.DateTimeField(null=True, blank=True)
    filename = models.CharField(max_length=100, blank=True)
    picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_claims_path, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    date_uploaded = models.DateTimeField(null=True, blank=True)

    @property
    def is_ready(self):
        return (self.offer.type == 'adoptable' and self.date_fulfilled != None) or (self.offer.type == 'icon' and not self.date_fulfilled and self.filename)

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def extension(self):
        return self.filename.split('.')[-1].lower()

    @property
    def thumbnail_path(self):
        if not self.picture:
            return None
        path = ('/').join(self.picture.path.split('/')[:-1])
        return '{0}/{1}.s.jpg'.format(path, self.id)

    @property
    def thumbnail_url(self):
        if os.path.exists(self.thumbnail_path):
            return '{0}Artwork/claims/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)
        return '{0}images/loading2.gif'.format(settings.STATIC_URL)

    @property
    def thumbnail_created(self):
        return os.path.exists(self.thumbnail_path)

    @property
    def url(self):
        return '{0}Artwork/claims/{1}.{2}'.format(settings.MEDIA_URL, self.id, self.extension)

    def save(self, update_thumbs=True, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(TradingClaim, self).save(*args, **kwargs)
        logger.info(self.picture)
        if update_thumbs:
            process_images.apply_async(('TradingClaim', self.id, 'small'), countdown=20)

    def delete(self, *args, **kwargs):
        if self.offer.type == 'icon':
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, self.picture.name))
                os.remove(os.path.join(settings.MEDIA_ROOT, self.thumbnail_path))
            except OSError:
                pass
        return super(TradingClaim, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('upload-claim', kwargs={'claim_id': self.id})

    class Meta:
        ordering = ['date_posted']


class PictureCharacter(models.Model):
    picture = models.ForeignKey('Picture', null=True, blank=True)
    pending = models.ForeignKey('Pending', null=True, blank=True)
    character = models.ForeignKey('Character', null=True, blank=True)
    date_tagged = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Tag(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    tag = models.CharField(max_length=255, blank=True)
#    num_pictures = models.IntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    def __unicode__(self):
        return self.tag

    class Meta:
        ordering = ['tag']


class GiftPicture(models.Model):
    sender = models.ForeignKey('User', null=True, blank=True)
    recipient = models.ForeignKey('User', null=True, blank=True, related_name='gifts_received')
    picture = models.ForeignKey('Picture', null=True, blank=True)
    filename = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    date_sent = models.DateTimeField(null=True, blank=True)
    date_accepted = models.DateTimeField(null=True, blank=True)
    hash = models.UUIDField(default=uuid.uuid4, null=True, blank=True)


class SocialMedia(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=16, blank=True)

    def __unicode__(self):
        return self.name


class SocialMediaIdentity(models.Model):
    social_media = models.ForeignKey('SocialMedia')
    user = models.ForeignKey('User', null=True, blank=True)
    identity = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return '{0}: {1}'.format(self.social_media, self.identity)

    class Meta:
        verbose_name_plural = 'social media identities'


class UnviewedPicture(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    picture = models.ForeignKey('Picture', null=True, blank=True)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='new_pictures')
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class ApprovalAccess(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    login = models.DateTimeField(null=True, blank=True)
    logout = models.DateTimeField(null=True, blank=True)


class AdminBlog(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    message = models.TextField(blank=True)


class ArtistName(models.Model):
    artist = models.ForeignKey('User', null=True, blank=True)
    date_changed = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    name = models.CharField(max_length=150, blank=True)


class Block(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, related_name='blocked_by')
    blocked_user = models.ForeignKey('User', null=True, blank=True)
    date_blocked = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Bulletin(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    date_published = models.DateTimeField(null=True, blank=True)
    title = models.TextField(blank=True)
    bulletin = models.TextField(blank=True)
    is_admin = models.BooleanField(default=False)
    show_email = models.BooleanField(default=False)


class Contest(models.Model):
    TYPE_CHOICES = (
        ('global', 'Global'),
        ('personal', 'Personal'),
    )

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    creator = models.ForeignKey('User', null=True, blank=True)
    title = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    rules = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_start = models.DateTimeField(null=True, blank=True)
    date_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    allow_multiple_entries = models.BooleanField(default=False)
    allow_anonymous_entries = models.BooleanField(default=False)
    allow_voting = models.BooleanField(default=False)

    def get_winner(self):
        try:
            return self.contestentry_set.annotate(vote_count=Count('contestvote')).order_by('-vote_count')[0]
        except IndexError:
            return None

    @property
    def is_ended(self):
        return self.date_end < timezone.now()

    @property
    def days_left(self):
        return (self.date_end - timezone.now()).days

    @property
    def winning_entries(self):
        entries = self.contestentry_set.all().order_by('?')
        if self.is_ended:
            entries = entries.annotate(votes=Count('contestvote')).order_by('-votes', 'date_entered')
        return entries[0:20]

    def get_absolute_url(self):
        return reverse('contest', kwargs={'contest_id': self.id})

    def __unicode__(self):
        return self.title


class ContestEntry(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    contest = models.ForeignKey('Contest', null=True, blank=True)
    picture = models.ForeignKey('Picture', null=True, blank=True)
    date_entered = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_notified = models.DateTimeField(null=True, blank=True)

    @property
    def num_votes(self):
        return self.contestvote_set.count()

    def get_absolute_url(self):
        return reverse('contest', kwargs={'contest_id': self.contest.id})

    def save(self, *args, **kwargs):
        try:
            return ContestEntry.objects.get(contest=self.contest, picture=self.picture)
        except ContestEntry.DoesNotExist:
            return super(ContestEntry, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'contest entries'
        ordering = ['-date_entered']


class ContestVote(models.Model):
    entry = models.ForeignKey('ContestEntry', null=True, blank=True)
    user = models.ForeignKey('User', null=True, blank=True)
    date_voted = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('contest', kwargs={'contest_id': self.entry.contest.id})


class PrivateMessage(models.Model):
    sender = models.ForeignKey('User', null=True, blank=True, related_name='pms_sent')
    recipient = models.ForeignKey('User', null=True, blank=True, related_name='pms_received')
    date_sent = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reply_to = models.ForeignKey('PrivateMessage', null=True, blank=True)
    subject = models.TextField(blank=True)
    message = models.TextField(blank=True)
    date_viewed = models.DateTimeField(null=True, blank=True)
    date_replied = models.DateTimeField(null=True, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)

    @property
    def quoted_message(self):
        return '\n\n\n[quote]\n{0}\n[/quote]'.format(self.message)

    class Meta:
        ordering = ['-date_sent']


class SpecialFeature(models.Model):
    keyword = models.CharField(max_length=32, blank=True)
    tag = models.ForeignKey('Tag', null=True, blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)

    @property
    def pictures(self):
        return Picture.objects.filter(id__in=Subquery(self.tag.picture_set.values_list('id', flat=True))).order_by('?')
#        return Picture.objects.filter(keywords__search=self.keyword).order_by('?')

    def __unicode__(self):
        return '{0} - {1}'.format(self.id, self.title)


class Vote(models.Model):
    voter = models.ForeignKey('User', null=True, blank=True, related_name='votes_cast')
    artist = models.ForeignKey('User', null=True, blank=True, related_name='votes_received')
