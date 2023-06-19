from django.conf import settings
from django.db import models, connection
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count, CharField
from django.db.models.functions import Lower
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.core.mail import mail_admins
#from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, UserManager, AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import uuid
import datetime
import pytz
import os
import re
import shutil
from PIL import Image
from pwd import getpwnam
from precise_bbcode.bbcode import get_parser
from user_agents import parse as parse_ua

from fanart.utils import dictfetchall, upperfirst, sizeof_fmt
from fanart.tasks import process_images

import logging
logger = logging.getLogger(__name__)

CharField.register_lookup(Lower, "lower")

THREE = 90

artists_tabs = ('name', 'newest', 'recentactive', 'toprated', 'topratedactive', 'prolific', 'random', 'search')
artwork_tabs = ('unviewed', 'newest', 'newestfaves', 'toprated', 'topratedrecent', 'random', 'search', 'tag', 'character')
characters_tabs = ('canon', 'newest', 'mosttagged', 'recentlytagged', 'charactername', 'artist', 'search')


def get_media_path(instance, filename):
    return '{0}/{1}'.format(instance.id, filename)

#def get_offers_path(instance, filename):
#    return 'Artwork/offers/{0}.{1}'.format(instance.id, instance.extension)

#def get_offers_thumb_path(instance, filename):
#    return 'Artwork/offers/{0}.s.jpg'.format(instance.id)

#def get_claims_path(instance, filename):
#    return 'Artwork/claims/{0}.{1}'.format(instance.id, instance.extension)

#def get_claims_thumb_path(instance, filename):
#    return 'Artwork/claims/{0}.s.jpg'.format(instance.id)

def get_profile_path(instance, filename):
    extension = filename.split('.')[-1].lower()
    filename = '{0}.{1}'.format(uuid.uuid4(), extension)
    return 'profiles/{0}'.format(filename)

def get_banner_path(instance, filename):
    extension = filename.split('.')[-1].lower()
    filename = '{0}.{1}'.format(uuid.uuid4(), extension)
    return 'banners/{0}'.format(filename)

def get_pending_path(instance, filename):
    return 'pending/{0}/{1}.{2}'.format(uuid.uuid4(), instance.sanitized_basename, instance.extension)

def get_featured_path(instance, filename):
    return 'featured/{0}/{1}'.format(instance.featured_artist.month_featured, filename)

def get_featured_banner_path(instance, filename):
    return 'featured/{0}/{1}'.format(instance.month_featured, filename)

#def get_coloring_path(instance, filename):
#    return 'Artwork/coloring/{0}.{1}'.format(instance.id, instance.extension)

#def get_coloring_thumb_path(instance, filename):
#    return 'Artwork/coloring/{0}.s.jpg'.format(instance.id)

#def get_image_thumb_small_path(instance, filename):
#    return '{0}/thumb_small/{1}'.format(instance.id, filename)
#
#def get_image_thumb_large_path(instance, filename):
#    return '{0}/thumb_large/{1}'.format(instance.id, filename)


def validate_unique_username(value):
    dir_name = make_dir_name(value)
    is_forbidden_name = dir_name in artists_tabs
    dir_name_already_exists_in_db = User.objects.filter(Q(username=value) | Q(dir_name__lower=dir_name.lower())).exists()

    if dir_name_already_exists_in_db or is_forbidden_name:
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


def make_dir_name(username):
    new_dir_name = User.normalize_username(username)
    new_dir_name = re.sub('&#[0-9]+;', 'x', new_dir_name)
    new_dir_name = re.sub("[\\']", '', new_dir_name)
    new_dir_name = re.sub('[^a-zA-Z0-9]', '_', new_dir_name)
    return new_dir_name


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class FanartUserManager(UserManager):

    @property
    def currently_online(self):
        recent_activity_cutoff_time = timezone.now() - datetime.timedelta(seconds=settings.RECENT_ACTIVITY_CUTOFF_SECS)
        return self.get_queryset().filter(last_active__gt=recent_activity_cutoff_time)

    def recently_active(self, request=None):
        artists = self.get_queryset().filter(is_artist=True, is_active=True, num_pictures__gt=0).order_by('-last_upload')
        if request:
            if request.user.is_authenticated:
                artists = artists.exclude(id__in=request.user.blocked_artist_ids)
            else:
                artists = artists.filter(is_public=True)
        return artists[0:10]

    def upcoming_birthdays(self):
        with connection.cursor() as cursor:
            try:
                query = """
SELECT `id`, `username`, `birth_date`, `dir_name`, `show_birthdate_age`, `num_pictures`,
    DATE_ADD(
        birth_date,
        INTERVAL IF(DAYOFYEAR(birth_date) >= DAYOFYEAR(CURDATE()),
            YEAR(CURDATE())-YEAR(birth_date),
            YEAR(CURDATE())-YEAR(birth_date)+1
        ) YEAR
    ) AS `next_birthday`,
    CAST((DATEDIFF(DATE_ADD(
        birth_date,
        INTERVAL IF(DAYOFYEAR(birth_date) >= DAYOFYEAR(CURDATE()),
            YEAR(CURDATE())-YEAR(birth_date),
            YEAR(CURDATE())-YEAR(birth_date)+1
        ) YEAR
    ), birth_date) / 365) AS UNSIGNED INTEGER) AS `age`
FROM `fanart_user`
WHERE
    `birth_date` IS NOT NULL
    AND `show_birthdate` = 1
    AND `is_active` = 1
    AND `is_artist` = 1
    AND `num_pictures` > 0
HAVING
    `next_birthday` BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
ORDER BY `next_birthday`
"""
                cursor.execute(query, [])
            except:
                query = """
SELECT `id`, `username`, `birth_date`, `birth_date` as `next_birthday`, `dir_name`, `show_birthdate_age`, 35 AS `age`
FROM `fanart_user`
WHERE
    `birth_date` IS NOT NULL
ORDER BY `next_birthday`
"""
                cursor.execute(query, [])
            result = dictfetchall(cursor)
        return result

    def create_user(self, username, email=None, password=None, is_artist=True, **extra_fields):
        user = super(FanartUserManager, self).create_user(username, email=email, password=password, **extra_fields)
        new_dir_name = make_dir_name(user.username)
        new_absolute_dir_name = '{0}/Artwork/Artists/{1}'.format(settings.MEDIA_ROOT, new_dir_name)
        try:
            os.mkdir(new_absolute_dir_name)
        except OSError:
            pass
        user.dir_name = new_dir_name
        user.sort_name = user.username
        user.is_artist = is_artist
        user.save()
        return user


class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-binary'),
        ('', '(No response)'),
    )

    THUMBNAILS_JPEG = False

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
#        validators=[username_validator],
#        validators=[validate_unique_username],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    last_host = models.CharField(max_length=128, null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True)
#    h_size = models.IntegerField(null=True, blank=True)
#    v_size = models.IntegerField(null=True, blank=True)
#    show_favorite_artists_box = models.BooleanField(default=True)
#    show_favorite_pictures_box = models.BooleanField(default=True)
#    show_sketcher_box = models.BooleanField(default=True)
#    show_community_art_box = models.BooleanField(default=True)
#    show_contests_box = models.BooleanField(default=True)
#    show_tool_box = models.BooleanField(default=True)
#    folders_tree = models.BooleanField(default=False)

    artist_id_orig = models.IntegerField(null=True, blank=True, db_index=True)

    dir_name = models.CharField(max_length=150, blank=True, db_index=True)
    sort_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True, help_text='Controls whether user is allowed to log in. Uncheck this to disable accounts.')
    is_artist = models.BooleanField(default=True, help_text='Controls whether user has a visible artist page and has access to artist modules in ArtManager, or simply a Profile for following others.')
    is_public = models.BooleanField(default=True, help_text='Controls whether user\'s art page is publicly visible to unauthenticated users')
    is_paid = models.BooleanField(default=True)
    is_under_probation = models.BooleanField(default=False)
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
    pronouns = models.CharField(max_length=30, blank=True)
    banner_text = models.TextField(blank=True)
    banner_text_updated = models.DateTimeField(null=True, blank=True)
    banner_text_min = models.TextField(blank=True)
#    zip_enabled = models.BooleanField(default=True)
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
    tooltips_enabled = models.BooleanField(default=True)

    profile_picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='profile_height', width_field='profile_width', upload_to=get_profile_path, null=True, blank=True)
    profile_width = models.IntegerField(null=True, blank=True)
    profile_height = models.IntegerField(null=True, blank=True)

    profile_pic_id = models.IntegerField(null=True, blank=True)
    profile_pic_ext = models.CharField(max_length=5, blank=True)
    banner = models.ForeignKey('Banner', null=True, blank=True, on_delete=models.SET_NULL)
#    old_banner_id = models.IntegerField(null=True, blank=True)
#    old_banner_ext = models.CharField(max_length=5, blank=True)
    example_pic = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    suspension_message = models.TextField(blank=True)
    auto_approve = models.BooleanField(default=False)
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
            return self.example_pic
        return self.picture_set.filter(date_deleted__isnull=True, is_public=True).order_by('?').first()

    @property
    def possessive_pronoun(self):
        if self.gender == 'male':
            return 'his'
        elif self.gender == 'female':
            return 'her'
        else:
            return 'their'

    @property
    def unread_received_pms_count(self):
        return self.pms_received.filter(date_viewed__isnull=True).count()

    @property
    def visible_fans(self):
        return self.fans.filter(is_visible=True)

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
AND fanart_user.is_active=1
AND fanart_user.is_artist=1
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
        recent_pictures_cutoff_date = timezone.now() - datetime.timedelta(days=settings.ARTIST_RECENT_PICTURES_DAYS)
        return self.picture_set.filter(is_public=True, date_deleted__isnull=True, date_uploaded__gt=recent_pictures_cutoff_date).order_by('-date_uploaded')[0:10]

    @property
    def blocked_commenters(self):
        return [b.blocked_user for b in self.blocked_users.all()]

    @property
    def blocked_artists(self):
        return self.blocked_commenters

    @property
    def blocked_artist_ids(self):
        return [u.id for u in self.blocked_artists]

    def is_blocked_by(self, blocking_user):
        return Block.objects.filter(blocked_user=self, user=blocking_user).exists()

    @property
    def is_blanket_blocked(self):
        return self.is_blocked_by(None)

    @property
    def unread_comments(self):
        return ThreadedComment.objects.filter(picture__artist=self, is_deleted=False, is_received=False).exclude(user=self).order_by('-date_posted')

    @property
    def unread_shouts(self):
        return Shout.objects.filter(artist=self, is_deleted=False, is_received=False).order_by('-date_posted')

    @property
    def date_joined_str(self):
        if self.date_joined < datetime.datetime(1999, 1, 1, tzinfo=pytz.utc):
            return None
        return self.date_joined

    @property
    def first_upload(self):
        try:
            return self.picture_set.all().order_by('date_uploaded').first().date_uploaded
        except AttributeError:
            return None

    @property
    def pictures_in_main_folder(self):
        return self.picture_set.filter(folder__isnull=True).count()

    @property
    def open_gifts_received(self):
        return self.gifts_received.filter(is_active=False)

    @property
    def icon_claims_ready(self):
        return self.icon_claims_received.filter(date_fulfilled__isnull=True)
#        return TradingClaim.objects.filter(offer__type='icon', user=self, offer__is_visible=True, date_fulfilled__isnull=True).exclude(filename='').order_by('-date_posted')

    @property
    def adoptable_claims_ready(self):
        return self.adoptable_claims_received.filter(offer__is_visible=True, offer__is_active=True, date_fulfilled__isnull=False)
#        return TradingClaim.objects.filter(offer__type='adoptable', user=self, offer__is_visible=True, date_fulfilled__isnull=False).order_by('-date_posted')

    @property
    def claims_ready(self):
        return self.icon_claims_ready.union(self.adoptable_claims_ready).order_by('-date_posted')

    @property
    def icon_claims_received(self):
#        return self.claim_set.filter(offer__type='icon', offer__is_visible=True).exclude(filename='').order_by('-date_posted')
        return self.claim_set.filter(offer__type='icon', offer__is_visible=True).exclude(filename='')

    @property
    def adoptable_claims_received(self):
#        return self.claim_set.filter(offer__type='adoptable').order_by('-date_posted')
        return self.claim_set.filter(offer__type='adoptable')

    @property
    def active_offers(self):
        return self.offer_set.filter(is_active=True, is_visible=True).order_by('-date_posted')

    @property
    def active_icon_offers(self):
        return self.active_offers.filter(type='icon')

    @property
    def active_adoptable_offers(self):
        return self.active_offers.filter(type='adoptable')

    @property
    def inactive_offers(self):
        return self.offer_set.exclude(is_active=True, is_visible=True).order_by('-date_posted')

    @property
    def banner_url(self):
        if self.banner:
            return self.banner.picture.url
#        elif self.old_banner_id:
#            return '{0}Artwork/banners/{1}.{2}'.format(settings.MEDIA_URL, self.old_banner_id, self.old_banner_ext)
        return None

    @property
    def has_profile_pic(self):
        return bool(self.profile_picture) or (bool(self.profile_pic_id) and bool(self.profile_pic_ext))

    @property
    def profile_pic_url(self):
        if self.profile_picture:
            if self.profile_pic_resized:
                return self.profile_picture.url
            return settings.SPINNER_IMG_URL
        if self.profile_pic_id and self.profile_pic_ext:
            return '{0}profiles/{1}.{2}'.format(settings.MEDIA_URL, self.profile_pic_id, self.profile_pic_ext)
        return settings.BLANKDOT_IMG_URL

    @property
    def profile_pic_thumbnail_url(self):
#        return '{0}profiles/{1}'.format(settings.MEDIA_URL, self.profile_pic_thumbnail)

        if self.profile_picture and self.profile_pic_thumbnail_created:
            return '{0}profiles/{1}'.format(settings.MEDIA_URL, self.profile_pic_thumbnail)
        elif self.profile_pic_id:
            return '{0}profiles/{1}.s.{2}'.format(settings.MEDIA_URL, self.profile_pic_id, self.profile_pic_ext)
        elif self.profile_picture:
            return settings.SPINNER_IMG_URL
        return None

    @property
    def profile_pic_thumbnail_created(self):
        return os.path.exists(self.profile_pic_thumbnail_path)

    @property
    def profile_pic_resized(self):
        if not self.profile_picture:
            return False
        try:
            im = Image.open(self.profile_picture.path)
            if im.width > settings.THUMB_SIZE['profile']:
                return False
        except IOError:
            return False
        return True

    @property
    def profile_pic_thumbnail_path(self):
        if self.profile_picture == None:
            return None
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

    @property
    def allow_sketcher(self):
        return not self.ban_set.exists()

    @property
    def days_since_joined(self):
        return (timezone.now() - self.date_joined).days

    @property
    def can_comment(self):
        return self.days_since_joined >= settings.USER_AGE_BEFORE_COMMENTING_DAYS

    def create_dir(self):
        try:
            os.mkdir(self.absolute_dir_name)
            www_uid = getpwnam(settings.WWW_USER).pw_uid
            os.chown(self.absolute_dir_name, www_uid, -1)
        except OSError:
            pass

    def create_deleted_dir(self):
        try:
            os.mkdir(os.path.join(self.absolute_dir_name, 'deleted'))
            www_uid = getpwnam(settings.WWW_USER).pw_uid
            os.chown(os.path.join(self.absolute_dir_name, 'deleted'), www_uid, -1)
        except OSError:
            pass

    @staticmethod
    def get_absolute_dir_name(dir_name):
        return '{0}/Artwork/Artists/{1}'.format(settings.MEDIA_ROOT, dir_name)

    def check_dir_name_for_os_collision(self, dir_name):
        absolute_dir_name = User.get_absolute_dir_name(dir_name)
        if os.path.isdir(absolute_dir_name):
            mail_admins(
                'Artist directory collision',
                f'Artist rename failed: {self.username} tried to create dir\n{absolute_dir_name}\nwhich already exists',
            )
            raise ValidationError(
                _('The directory name %(value)s is already in use. This may be a data error; please contact the '
                  'administrator for assistance.'),
                params={'value': dir_name},
            )

    def change_dir_name(self):
        new_dir_name = make_dir_name(self.username)
#        new_dir_name = re.sub('&#[0-9]+;', 'x', self.username)
#        new_dir_name = re.sub("[\\']", '', new_dir_name)
#        new_dir_name = re.sub('[^a-zA-Z0-9]', '_', new_dir_name)

        if new_dir_name == self.dir_name:
            return self.dir_name

        new_absolute_dir_name = User.get_absolute_dir_name(new_dir_name)
        self.check_dir_name_for_os_collision(new_dir_name)

        os.rename(self.absolute_dir_name, new_absolute_dir_name)
        self.dir_name = new_dir_name
        self.save()

        return new_dir_name

    def refresh_num_pictures(self):
        self.num_pictures = self.picture_set.count()
        self.save()

    def refresh_picture_ranks(self):
        pictures = self.picture_set.order_by('date_uploaded')
        for i, picture in enumerate(pictures):
            picture.rank_in_artist = i + 1
            picture.save()

    def refresh_main_folder_picture_ranks(self):
        pictures = self.picture_set.filter(folder=None).order_by('date_uploaded')
        for i, picture in enumerate(pictures):
            picture.rank_in_folder = i + 1
            picture.save()

    def refresh_num_characters(self):
        self.num_characters = self.character_set.count()
        self.save()

    def refresh_num_faves(self):
        self.num_faves = self.fans.count()
        num_favepics = 0
        for picture in self.picture_set.all():
            num_favepics += picture.num_faves
        self.num_favepics = num_favepics
        self.save()

    def update_last_active(self):
        self.last_active = timezone.now()
        self.save()

    def save(self, update_thumbs=False, *args, **kwargs):
        logger.debug('Saving {0}, {1}'.format(self, update_thumbs))

        if not os.path.exists(self.absolute_dir_name):
            self.create_dir()
            logger.info('Creating {0}'.format(self.absolute_dir_name))

        super(User, self).save(*args, **kwargs)
        if update_thumbs:
            process_images('fanart.models', 'User', self.id, 'small')
            if self.profile_width > settings.THUMB_SIZE['profile'] or self.profile_height > settings.THUMB_SIZE['profile']:
                process_images.apply_async(('fanart.models', 'User', self.id, 'profile'), countdown=20)

    def delete(self, *args, **kwargs):
        shutil.rmtree(self.absolute_dir_name, ignore_errors=True)
        return super(User, self).delete(*args, **kwargs)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.id, self.username, self.email)


class PictureManager(models.Manager):

    @property
    def random_popular(self):
        return self.filter(num_faves__gt=20).exclude(mime_type__in=list(settings.MOVIE_FILE_TYPES.keys())).order_by('?')

    @property
    def most_popular_recent(self):
        date_cutoff = timezone.now() - datetime.timedelta(days=600)
        min_faves = 10
        return Picture.objects.filter(num_faves__gt=min_faves, date_uploaded__gt=date_cutoff).exclude(mime_type__in=list(settings.MOVIE_FILE_TYPES.keys())).order_by('-num_faves')

    @property
    def extensions_in_use(self):
        return set([pic.extension for pic in self.get_queryset()])

    def get_queryset(self):
        return super(PictureManager, self).get_queryset().exclude(date_deleted__isnull=False).exclude(artist__is_artist=False)


class Picture(models.Model):

    THUMBNAILS_JPEG = True

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=255, blank=True)
    original_filename = models.CharField(max_length=255, blank=True, default='')
#    extension = models.CharField(max_length=5, blank=True)
    title = models.TextField(blank=True)
    is_color = models.BooleanField(default=True)
    type = models.CharField(max_length=32, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.IntegerField(blank=True)
    quality = models.CharField(max_length=1, blank=True)
#    thumb_height = models.IntegerField(blank=True)
    num_comments = models.IntegerField(default=0)
    num_faves = models.IntegerField(default=0)
#    characters = models.CharField(max_length=50, blank=True)
    width = models.IntegerField(blank=True)
    height = models.IntegerField(blank=True)
    date_uploaded = models.DateTimeField(null=True, blank=True, db_index=True)
    date_approved = models.DateTimeField(null=True, blank=True, db_index=True)
    date_updated = models.DateTimeField(null=True, blank=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    hash = models.UUIDField(null=True, blank=True, editable=False, db_index=True)
    is_public = models.BooleanField(default=True)
    rank_in_artist = models.IntegerField(default=0)
    rank_in_folder = models.IntegerField(default=0)
    approved_by = models.ForeignKey('User', null=True, blank=True, related_name='inserted', on_delete=models.SET_NULL)
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
    def extension(self):
        if self.filename:
            return self.filename.split('.')[-1].lower()
        return self.picture.name.split('.')[-1].lower()

    @property
    def thumbnail_extension(self):
        if self.is_movie or self.THUMBNAILS_JPEG:
            return 'jpg'
        return self.extension

#    @property
#    def preview_extension(self):
#        if self.mime_type in ['image/jpeg', 'image/png', 'image/gif']:
#            return self.extension
##            return 'p.{0}'.format(self.extension)
#        return 'p.jpg'

    @property
    def is_movie(self):
        return self.mime_type in list(settings.MOVIE_FILE_TYPES.keys())

    @property
    def video_width(self):
        if not self.width:
            return 700
        return self.width

    @property
    def video_height(self):
        if not self.height:
            return 500
        return self.height

    @property
    def thumbnail_url(self):
        return '{0}Artwork/Artists/{1}/{2}.s.{3}'.format(settings.MEDIA_URL, self.artist.dir_name, self.basename, self.thumbnail_extension)

    @property
    def preview_url(self):
        return '{0}Artwork/Artists/{1}/{2}.p.{3}'.format(settings.MEDIA_URL, self.artist.dir_name, self.basename, self.thumbnail_extension)

    @property
    def path(self):
        return '{0}/{1}'.format(self.artist.absolute_dir_name, self.filename)

    @property
    def thumbnail_path(self):
        return self.thumbnail_path_legacy

    @property
    def thumbnail_path_legacy(self):
        return '{0}/{1}.s.jpg'.format(self.artist.absolute_dir_name, self.basename)

    @property
    def thumbnail_path_corrected(self):
        return '{0}/{1}.s.{2}'.format(self.artist.absolute_dir_name, self.basename, self.thumbnail_extension)

    @property
    def preview_path(self):
        return self.preview_path_legacy

    @property
    def preview_path_legacy(self):
        return '{0}/{1}.p.jpg'.format(self.artist.absolute_dir_name, self.basename)

    @property
    def preview_path_corrected(self):
        return '{0}/{1}.p.{2}'.format(self.artist.absolute_dir_name, self.basename, self.thumbnail_extension)

    @property
    def url(self):
        return '{0}Artwork/Artists/{1}/{2}'.format(settings.MEDIA_URL, self.artist.dir_name, self.filename)

    @property
    def preview_width(self):
        return settings.THUMB_SIZE['large']

    @property
    def preview_height(self):
        return int(self.height * settings.THUMB_SIZE['large'] / self.width)

    @property
    def thumb_height(self):
        return int(self.height * settings.THUMB_SIZE['small'] / self.width)

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
            return Picture.objects.filter(artist=self.artist, folder=None)
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

    @property
    def year(self):
        return self.date_uploaded.year

    @property
    def date_featured(self):
        featured = self.featuredpicture_set.first()
        if featured:
            return featured.date_featured
        return None

    @property
    def featured_picture(self):
        return self.featuredpicture_set.first()

    def get_absolute_url(self):
        # return reverse('artmanager:artwork-picture-detail', kwargs={'picture_id': self.id})
        return reverse('picture', kwargs={'picture_id': self.id})

    def set_deleted(self):

        UnviewedPicture.objects.filter(picture=self).delete()

        for character in Character.objects.filter(profile_picture=self):
            character.profile_picture = None
            character.save()

        if self.artist.example_pic == self:
            self.artist.example_pic = None
            self.artist.save()

        self.date_deleted = timezone.now()
        self.save()

        self.artist.refresh_num_pictures()
        self.artist.refresh_picture_ranks()
        if self.folder:
            self.folder.refresh_picture_ranks()
            self.folder.refresh_num_pictures()
        else:
            self.artist.refresh_main_folder_picture_ranks()

        self.artist.create_deleted_dir()
        hash = uuid.uuid4()
        deleted_filename = '.'.join([self.basename, str(hash), self.extension])
        deleted_thumbnail_filename = '.'.join([self.basename, str(hash), 's', self.thumbnail_extension])
        deleted_preview_filename = '.'.join([self.basename, str(hash), 'p', self.thumbnail_extension])
        try:
            os.rename(self.path, os.path.join(self.artist.absolute_dir_name, 'deleted', deleted_filename))
        except OSError:
            pass
        try:
            os.rename(self.thumbnail_path, os.path.join(self.artist.absolute_dir_name, 'deleted', deleted_thumbnail_filename))
        except OSError:
            pass
        try:
            os.rename(self.preview_path, os.path.join(self.artist.absolute_dir_name, 'deleted', deleted_preview_filename))
        except OSError:
            pass

        logger.info('Picture {0} by {1} was deleted.'.format(self, self.artist))

    def refresh_num_faves(self):
        self.num_faves = self.fans.count()
        self.save()

    def replace_urls(self):
        for url in REPLACEMENT_URLS:
            pattern, replacement = url
            self.title = re.sub(pattern, replacement, self.title)

    def __str__(self):
        return '{0}: {1} {2}'.format(self.artist.username, self.id, self.filename)


class Folder(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.SET_NULL)
    num_pictures = models.IntegerField(default=0)

    @property
    def latest_picture(self):
        return self.picture_set.order_by('-date_uploaded').first()

    def refresh_num_pictures(self):
        logger.info('Refreshing folder: {0}'.format(self))
        self.num_pictures = self.picture_set.count()
        self.save()

    def refresh_picture_ranks(self):
        pictures = self.picture_set.filter(folder=self).order_by('date_uploaded')
        for i, picture in enumerate(pictures):
            picture.rank_in_folder = i + 1
#            logger.info('{0} {1}'.format(picture, picture.rank_in_folder))
            picture.save()

    def get_absolute_url(self):
        return reverse('artist-gallery', kwargs={'dir_name': self.user.dir_name})

    def delete(self, *args, **kwargs):
        for picture in self.picture_set.all():
            picture.folder = self.parent
            picture.save()
        for pending in self.pending_set.all():
            pending.folder = self.parent
            pending.save()
        for folder in self.folder_set.all():
            folder.parent = self.parent
            folder.save()

        if self.parent:
            self.parent.refresh_picture_ranks()
            self.parent.refresh_num_pictures()
        else:
            self.user.refresh_main_folder_picture_ranks()
        super(Folder, self).delete(*args, **kwargs)

    def __str__(self):
        return '{0} {1}'.format(self.id, self.name)


class BaseComment(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    hash = models.CharField(max_length=36, null=True, blank=True)

    def __str__(self):
        return '{0} {1}'.format(self.id, self.user.username)

    @property
    def is_comment(self):
        return isinstance(self, ThreadedComment)

    @property
    def is_shout(self):
        return isinstance(self, Shout)

    class Meta:
        abstract = True
        ordering = ['date_posted']


class ThreadedComment(BaseComment):
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    bulletin = models.ForeignKey('Bulletin', null=True, blank=True, on_delete=models.SET_NULL)
    reply_to = models.ForeignKey('ThreadedComment', null=True, blank=True, related_name='replies', on_delete=models.SET_NULL)

    @property
    def num_replies(self):
        return self.replies.count()

    def get_absolute_url(self):
        if self.bulletin:
            return reverse('bulletin', kwargs={'bulletin_id': self.bulletin.id})
        return reverse('comments', kwargs={'picture_id': self.picture.id})

    def __str__(self):
        if self.bulletin:
            return '{0} {1} on {2} by {3}'.format(self.id, self.user.username, self.bulletin, self.bulletin.user.username)
        return '{0} {1} on {2} by {3}'.format(self.id, self.user.username, self.picture, self.picture.artist.username)


class ShoutManager(models.Manager):

    def get_queryset(self):
        return super(ShoutManager, self).get_queryset().exclude(is_deleted=True)


class Shout(BaseComment):
    artist = models.ForeignKey('User', null=True, blank=True, related_name='shouts_received', on_delete=models.SET_NULL)
    reply_to = models.ForeignKey('Shout', null=True, blank=True, related_name='replies', on_delete=models.SET_NULL)

    objects = ShoutManager()

    @property
    def num_replies(self):
        return self.replies.count()

    @property
    def quoted_comment(self):
        return '\n\n\n[quote]\n{0}\n[/quote]'.format(self.comment)

    def get_absolute_url(self):
        return reverse('shouts', kwargs={'artist_id': self.artist.id})

    def __str__(self):
        return '{0} {1} on {2}'.format(self.id, self.user.username, self.artist.username)


class SpamFlag(models.Model):
    comment = models.ForeignKey('fanart.ThreadedComment', null=True, on_delete=models.CASCADE)
    shout = models.ForeignKey('fanart.Shout', null=True, on_delete=models.CASCADE)
    flagged_at = models.DateTimeField(auto_now_add=True)
    flagged_by = models.ForeignKey('fanart.User', on_delete=models.CASCADE)


class CharacterManager(models.Manager):

    def get_queryset(self):
        return super(CharacterManager, self).get_queryset().exclude(date_deleted__isnull=False)


class Character(models.Model):
    class Gender(models.TextChoices):
        MALE = ('male', 'Male')
        FEMALE = ('female', 'Female')
        NEITHER = ('', 'Neither')

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    creator = models.ForeignKey('User', null=True, related_name='characters_created', on_delete=models.SET_NULL)
    owner = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    is_canon = models.BooleanField(default=False)
    adopted_from = models.ForeignKey('User', null=True, blank=True, related_name='characters_adopted_out', on_delete=models.SET_NULL)
    name = models.CharField(max_length=64, blank=True)
    profile_picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    profile_coloring_picture = models.ForeignKey('coloring_cave.ColoringPicture', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    species = models.CharField(max_length=64, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    story_title = models.CharField(max_length=100, blank=True)
    story_url = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_modified = models.DateTimeField(null=True, blank=True)
    date_adopted = models.DateTimeField(null=True, blank=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    date_tagged = models.DateTimeField(null=True, blank=True)
    num_pictures = models.IntegerField(null=True, blank=True)

    objects = CharacterManager()

    @property
    def last_tagged(self):
        return self.picturecharacter_set.order_by('-date_tagged').first()

    @property
    def picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        elif self.profile_coloring_picture:
            return self.profile_coloring_picture.url
        elif self.is_canon:
            for ext in ['gif', 'jpg', 'png']:
                if os.path.exists('{0}/images/canon_characters/{1}.{2}'.format(settings.MEDIA_ROOT, self.id, ext)):
                    return '{0}canon_characters/{1}.{2}'.format(settings.MEDIA_URL, self.id, ext)
            return settings.CHARACTER_PLACEHOLDER_IMG_URL
        else:
            return settings.CHARACTER_PLACEHOLDER_IMG_URL

    @property
    def thumbnail_url(self):
        if self.profile_picture:
            return self.profile_picture.thumbnail_url
        elif self.profile_coloring_picture:
            return self.profile_coloring_picture.thumbnail_url
        elif self.is_canon:
            for ext in ['gif', 'jpg', 'png']:
                if os.path.exists('{0}/images/canon_characters/{1}.s.jpg'.format(settings.MEDIA_ROOT, self.id)):
                    return '{0}canon_characters/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)
            return settings.CHARACTER_PLACEHOLDER_IMG_URL
        else:
            return settings.CHARACTER_PLACEHOLDER_IMG_URL

    @property
    def preview_url(self):
        if self.profile_picture:
            return self.profile_picture.preview_url
        elif self.profile_coloring_picture:
            return self.profile_coloring_picture.preview_url
        elif self.is_canon:
            for ext in ['gif', 'jpg', 'png']:
                if os.path.exists('{0}/images/canon_characters/{1}.p.jpg'.format(settings.MEDIA_ROOT, self.id)):
                    return '{0}canon_characters/{1}.p.jpg'.format(settings.MEDIA_URL, self.id)
            return settings.CHARACTER_PLACEHOLDER_IMG_URL
        else:
            return settings.CHARACTER_PLACEHOLDER_IMG_URL

    @property
    def adoption_offer(self):
        return self.offer_set.filter(is_active=True, is_visible=True).first()

    @property
    def is_up_for_adoption(self):
        return self.offer_set.filter(is_active=True, is_visible=True).exists()

    def refresh_num_pictures(self):
        self.num_pictures = self.picturecharacter_set.count()
        self.save()

    def set_deleted(self):

        for offer in self.offer_set.all():
            offer.is_active = False
            offer.is_visible = False
            offer.save

        self.date_deleted = timezone.now()
        self.save()

        self.owner.refresh_num_characters()

        logger.info('Character {0} by {1} was deleted.'.format(self, self.owner))

    def __str__(self):
        return '{0} {1} ({2})'.format(self.id, self.name, self.owner)

    class Meta:
        ordering = ['name']


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
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='fans', on_delete=models.SET_NULL)
    picture = models.ForeignKey('Picture', null=True, blank=True, related_name='fans', on_delete=models.SET_NULL)
    character = models.ForeignKey('Character', null=True, blank=True, related_name='fans', on_delete=models.SET_NULL)
    is_visible = models.BooleanField(default=False)
    date_added = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    last_viewed = models.DateTimeField(null=True, blank=True)

    objects = FavoriteManager()

    class Meta:
        ordering = ['-date_added']


class PendingManager(models.Manager):

    def requiring_approval(self):
        return self.get_queryset().filter(is_approved=False).exclude(
            Q(artist__auto_approve=True) & ~(
                Q(force_approve=True) |
                Q(width__gt=settings.APPROVAL_TRIGGER_WIDTH) |
                Q(height__gt=settings.APPROVAL_TRIGGER_HEIGHT) |
                Q(file_size__gt=settings.APPROVAL_TRIGGER_SIZE) |
                Q(is_movie=True)
            )
        ).order_by('date_uploaded')


class Pending(models.Model):

    THUMBNAILS_JPEG = True

    artist = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.SET_NULL)
    picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_pending_path, null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True, default='')
    original_filename = models.CharField(max_length=255, blank=True, default='')
#    extension = models.CharField(max_length=5, blank=True, default='')
    mime_type = models.CharField(max_length=32, blank=True)
    is_movie = models.BooleanField(default=False)
    has_thumb = models.BooleanField(default=False)
    title = models.TextField(blank=True)
    width = models.IntegerField(null=True, blank=True, default=0)
    height = models.IntegerField(null=True, blank=True, default=0)
    file_size = models.IntegerField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    hash = models.UUIDField(null=True, blank=True, editable=False, db_index=True)
    notify_on_approval = models.BooleanField(default=False)
    work_in_progress = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    replaces_picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    reset_upload_date = models.BooleanField(default=False)
    notify_fans_of_replacement = models.BooleanField(default=False)
    keywords = models.TextField(blank=True)
    status = models.TextField(blank=True)
    remote_host = models.CharField(max_length=100, blank=True)
    remote_addr = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    force_approve = models.BooleanField(default=False)
    is_scanned = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    failed_processing = models.BooleanField(default=False)
    approved_by = models.ForeignKey('User', null=True, blank=True, related_name='approved_pictures', on_delete=models.SET_NULL)
    locked_for_publish = models.BooleanField(default=False)

    objects = PendingManager()

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def extension(self):
        if self.filename:
            return self.filename.split('.')[-1].lower()
        return self.picture.name.split('.')[-1].lower()

    @property
    def thumbnail_extension(self):
        if self.is_movie or self.THUMBNAILS_JPEG:
            return 'jpg'
        return self.extension

    @property
    def directory(self):
        if self.picture:
            return self.picture.name.split('/')[1]
        return None

    @property
    def thumbnail_url(self):
        if self.failed_processing:
            return settings.FAILED_PROCESSING_IMG_URL
        if self.is_movie:
            if self.has_thumb:
                return '{0}pending/{1}/{2}.s.{3}'.format(settings.MEDIA_URL, self.directory, self.sanitized_basename, self.thumbnail_extension)
            return settings.MOVIE_ICON_IMG_URL
        if os.path.exists(self.thumbnail_path):
            return '{0}pending/{1}/{2}.s.{3}'.format(settings.MEDIA_URL, self.directory, self.sanitized_basename, self.thumbnail_extension)
        return settings.SPINNER_IMG_URL

    @property
    def preview_url(self):
        if self.failed_processing:
            return settings.FAILED_PROCESSING_IMG_URL
        if self.is_movie:
            if self.has_thumb:
                return '{0}pending/{1}/{2}.p.{3}'.format(settings.MEDIA_URL, self.directory, self.sanitized_basename, self.thumbnail_extension)
            return settings.MOVIE_ICON_IMG_URL
        if os.path.exists(self.preview_path):
            return '{0}pending/{1}/{2}.p.{3}'.format(settings.MEDIA_URL, self.directory, self.sanitized_basename, self.thumbnail_extension)
        return settings.SPINNER_IMG_URL

    @property
    def thumbnail_path(self):
        path_parts = self.picture.name.split('/')
        path = '/'.join(path_parts[:-1])
        filename_parts = path_parts[-1].split('.')
        basename = '.'.join(filename_parts[:-1])
        extension = filename_parts[-1].lower()
        return '{0}/{1}/{2}.s.{3}'.format(settings.MEDIA_ROOT, path, basename, self.thumbnail_extension)

    @property
    def preview_path(self):
        path_parts = self.picture.name.split('/')
        path = '/'.join(path_parts[:-1])
        filename_parts = path_parts[-1].split('.')
        basename = '.'.join(filename_parts[:-1])
        extension = filename_parts[-1].lower()
        return '{0}/{1}/{2}.p.{3}'.format(settings.MEDIA_ROOT, path, basename, self.thumbnail_extension)

    @property
    def thumbnail_created(self):
        if self.is_movie:
            return True
        return os.path.exists(self.thumbnail_path)

    @property
    def preview_created(self):
        return os.path.exists(self.preview_path)

    @property
    def dimensions_warning(self):
        if not self.width or not self.height:
            return False
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

    @property
    def sanitized_basename(self):
        base_fn = re.sub('\.[^\.]+$', '', self.filename)
        out_fn = ''.join([upperfirst(part) for part in re.split('[- _+~&()\.]', base_fn)])
        out_fn = re.sub('[^a-zA-Z0-9_-]', '', out_fn)
        out_fn = re.sub('(?i)copy$', '', out_fn)
        out_fn = re.sub('(?i)jpg$', '', out_fn)
        out_fn = re.sub('(?i)gif$', '', out_fn)
        out_fn = re.sub('(?i)png$', '', out_fn)
        out_fn = re.sub('(?i)tlk$', 'TLK', out_fn)
        out_fn = re.sub('(?i)tlkfaa$', 'TLKFAA', out_fn)
        out_fn = re.sub('(?i)icon$', 'Icon', out_fn)
        return out_fn

    @property
    def sanitized_filename(self):
        return '{0}.{1}'.format(self.sanitized_basename, self.extension)

    @property
    def next_unique_basename(self):
        matching_basename_exists = False
        for extension in self.artist.picture_set.extensions_in_use:
            filename_to_test = f'{self.sanitized_basename}.{extension}'
            if not matching_basename_exists and self.artist.picture_set.filter(filename=filename_to_test).exists():
                matching_basename_exists = True
        if not matching_basename_exists:
            return self.sanitized_basename

        raw_basename = re.sub('[0-9]+$', '', self.sanitized_basename)
        highest_match = 0
        matched_input = False

        for picture in self.artist.picture_set.filter(filename__startswith=raw_basename):
            if picture.basename == raw_basename:
                matched_input = True
            match = re.match('{0}([0-9]*)'.format(raw_basename), picture.basename)
            if match:
                try:
                    trailing_number = int(match.group(1))
                except ValueError:
                    trailing_number = 0
                if trailing_number > highest_match:
                    highest_match = trailing_number
        if not matched_input:
            return raw_basename
        return '{0}{1}'.format(raw_basename, highest_match + 1)

    @property
    def requires_approval(self):
        return Pending.objects.requiring_approval().filter(pk=self.pk).exists()

    @property
    def approval_required_reasons(self):
        reasons = []
        if not self.requires_approval:
            return reasons
        if self.force_approve:
            reasons.append('Picture is voluntarily marked for manual approval.')
        if self.width and self.width > settings.APPROVAL_TRIGGER_WIDTH:
            reasons.append('Width is greater than {0} px.'.format(settings.APPROVAL_TRIGGER_WIDTH))
        if self.height and self.height > settings.APPROVAL_TRIGGER_HEIGHT:
            reasons.append('Height is greater than {0} px.'.format(settings.APPROVAL_TRIGGER_HEIGHT))
        if self.file_size and self.file_size > settings.APPROVAL_TRIGGER_SIZE:
            approval_trigger_size_humanized = sizeof_fmt(settings.APPROVAL_TRIGGER_SIZE)
            reasons.append('Size is greater than {0}.'.format(approval_trigger_size_humanized))
        if self.is_movie:
            reasons.append('Movie files must be manually approved.')
        return reasons

    @property
    def title_parsed(self):
        parser = get_parser()
        return parser.render(self.title)

    def get_absolute_url(self):
        return reverse('artmanager:pending-detail', kwargs={'pending_id': self.id})

    def save(self, update_thumbs=False, *args, **kwargs):
        if self.picture:
            self.file_size = self.picture.size
        super(Pending, self).save(*args, **kwargs)
        if update_thumbs:
            process_images.apply_async(('fanart.models', 'Pending', self.id, 'small'), countdown=20)
            process_images.apply_async(('fanart.models', 'Pending', self.id, 'large'), countdown=20)

    def delete(self, *args, **kwargs):
        if self.picture:
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'pending', self.directory), ignore_errors=True)
        super(Pending, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Pending {0} - {1} - {2}'.format(self.id, self.filename, self.artist.username)

    class Meta:
        ordering = ['date_uploaded']


class PictureCharacter(models.Model):
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.CASCADE)
    pending = models.ForeignKey('Pending', null=True, blank=True, on_delete=models.CASCADE)
    character = models.ForeignKey('Character', null=True, blank=True, on_delete=models.CASCADE)
    date_tagged = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, update_thumbs=False, *args, **kwargs):
        self.character.date_tagged = timezone.now()
        self.character.save()
        super(PictureCharacter, self).save(*args, **kwargs)


class Tag(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    tag = models.CharField(max_length=255, blank=True)
#    num_pictures = models.IntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ['tag']


class GiftPicture(models.Model):
    sender = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    recipient = models.ForeignKey('User', null=True, blank=True, related_name='gifts_received', on_delete=models.SET_NULL)
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    reply_message = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_accepted = models.DateTimeField(null=True, blank=True)
    date_declined = models.DateTimeField(null=True, blank=True)
    hash = models.UUIDField(default=uuid.uuid4, null=True, blank=True, db_index=True)

    @property
    def total_recipients(self):
        return self.picture.giftpicture_set.count()


class SocialMedia(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return self.name


class SocialMediaIdentity(models.Model):
    social_media = models.ForeignKey('SocialMedia', on_delete=models.CASCADE)
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    identity = models.CharField(max_length=100, blank=True)

    @property
    def display_identity(self):
        if self.identity.startswith('http'):
            url_parts = self.identity.split('/')
            return f'<a target="_blank" href="{self.identity}">{url_parts[-1]}</a>'
        return self.identity

    def __str__(self):
        return '{0}: {1}'.format(self.social_media, self.identity)

    class Meta:
        verbose_name_plural = 'social media identities'


class UnviewedPicture(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='new_pictures', on_delete=models.SET_NULL)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class ApprovalAccess(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    login = models.DateTimeField(null=True, blank=True)
    logout = models.DateTimeField(null=True, blank=True)


class AdminBlog(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    message = models.TextField(blank=True)


class ArtistName(models.Model):
    artist = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    date_changed = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    name = models.CharField(max_length=150, blank=True)


class Block(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, related_name='blocked_users', on_delete=models.SET_NULL)
    blocked_user = models.ForeignKey('User', null=True, blank=True, related_name='blocks_received', on_delete=models.SET_NULL)
    date_blocked = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-date_blocked']


class Bulletin(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    date_published = models.DateTimeField(null=True, blank=True)
    title = models.TextField(blank=True)
    bulletin = models.TextField(blank=True)
    is_admin = models.BooleanField(default=False)
    show_email = models.BooleanField(default=False)
    allow_replies = models.BooleanField(default=True)

    @property
    def quoted_comment(self):
        return '\n\n\n[quote]\n{0}\n[/quote]'.format(self.bulletin)

    @property
    def num_replies(self):
        return self.threadedcomment_set.count()

    def get_absolute_url(self):
        return reverse('bulletin', kwargs={'bulletin_id': self.id})

    def __str__(self):
        if self.user:
            return '{0}: {1} {2}'.format(self.user.username, self.id, self.title)
        return '{0} {1}'.format(self.id, self.title)


class Contest(models.Model):
    TYPE_CHOICES = (
        ('global', 'Global'),
        ('personal', 'Personal'),
    )

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    creator = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=64)
    description = models.TextField()
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
    def hours_left(self):
        return int((self.date_end - timezone.now()).seconds / 3600)

    @property
    def winning_entries(self):
        entries = self.contestentry_set.all().order_by('?')
        if self.is_ended:
            entries = entries.annotate(votes=Count('contestvote')).order_by('-votes', 'date_entered')
        return entries

    @property
    def total_votes(self):
        votes = 0
        for entry in self.contestentry_set.all():
            votes += entry.num_votes
        return votes

    def get_absolute_url(self):
        return reverse('contest', kwargs={'contest_id': self.id})

    def __str__(self):
        return self.title


class ContestEntry(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    contest = models.ForeignKey('Contest', null=True, blank=True, on_delete=models.CASCADE)
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    date_entered = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_notified = models.DateTimeField(null=True, blank=True)

    @property
    def num_votes(self):
        return self.contestvote_set.count()

    @property
    def is_runner_up(self):
        return self != self.contest.winning_entries[0]

    def get_absolute_url(self):
        return reverse('contest', kwargs={'contest_id': self.contest.id})

    def save(self, *args, **kwargs):
        try:
            return ContestEntry.objects.exclude(pk=self.pk).get(contest=self.contest, picture=self.picture).save()
        except ContestEntry.DoesNotExist:
            return super(ContestEntry, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'contest entries'
        ordering = ['-date_entered']

    def __str__(self):
        return '{0} {1} {2}'.format(self.id, self.contest, self.picture)


class ContestVote(models.Model):
    entry = models.ForeignKey('ContestEntry', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    date_voted = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('contest', kwargs={'contest_id': self.entry.contest.id})


class Showcase(models.Model):
    keyword = models.CharField(max_length=32, blank=True)
    tag = models.ForeignKey('Tag', null=True, blank=True, on_delete=models.SET_NULL)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)

    @property
    def pictures(self):
        return Picture.objects.filter(id__in=Subquery(self.tag.picture_set.values_list('id', flat=True)), artist__is_active=True).order_by('?')
#        return Picture.objects.filter(keywords__search=self.keyword).order_by('?')

    def __str__(self):
        return '{0} - {1}'.format(self.id, self.title)


class Vote(models.Model):
    voter = models.ForeignKey('User', null=True, blank=True, related_name='votes_cast', on_delete=models.SET_NULL)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='votes_received', on_delete=models.SET_NULL)
    date_voted = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # Count votes:
    # models.User.objects.filter(featured__isnull=True).values('id', 'username').annotate(num_votes=Count('votes_received')).filter(num_votes__gt=0).order_by('-num_votes')

class CustomIcon(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    icon_id = models.IntegerField(null=True, blank=True)
    extension = models.CharField(max_length=3, blank=True)
    type = models.IntegerField(null=True, blank=True)

    @property
    def icon_url(self):
        return '{0}Artwork/Artists/icons/{1}.{2}'.format(settings.MEDIA_URL, self.icon_id, self.extension)

    class Meta:
        ordering = ['type']


class Banner(models.Model):
    picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_banner_path, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class FeaturedArtist(models.Model):
    artist = models.ForeignKey('User', on_delete=models.CASCADE)
    date_featured = models.DateField()
    intro_text = models.TextField(blank=True, default='')
    own_words_text = models.TextField(blank=True, default='')
    analysis_text = models.TextField(blank=True, default='')
    is_published = models.BooleanField(default=False)
    banner = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='banner_height', width_field='banner_width', upload_to=get_featured_banner_path, null=True, blank=True)
    banner_width = models.IntegerField(null=True, blank=True)
    banner_height = models.IntegerField(null=True, blank=True)

    @property
    def month_featured(self):
        return self.date_featured.strftime('%Y-%m')

    @property
    def intro_text_parsed(self):
        return self.intro_text.replace('A_NAME', self.artist.username)

    @property
    def analysis_text_parsed(self):
        return self.analysis_text.replace('A_NAME', self.artist.username)

    def __str__(self):
        return '{0} {1}'.format(self.month_featured, self.artist.username)

    class Meta:
        ordering = ['-date_featured']


class FeaturedArtistPicture(models.Model):
    featured_artist = models.ForeignKey('FeaturedArtist', on_delete=models.CASCADE)
    showcase_picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_featured_path, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def basename(self):
        path_parts = self.showcase_picture.name.split('/')
        path = '/'.join(path_parts[:-1])
        filename_parts = path_parts[-1].split('.')
        return '.'.join(filename_parts[:-1])

    @property
    def thumbnail_url(self):
        return '{0}featured/{1}/{2}.s.jpg'.format(settings.MEDIA_URL, self.featured_artist.month_featured, self.basename)

    @property
    def thumbnail_path(self):
        path_parts = self.showcase_picture.name.split('/')
        path = '/'.join(path_parts[:-1])
        filename_parts = path_parts[-1].split('.')
        basename = '.'.join(filename_parts[:-1])
        extension = filename_parts[-1].lower()
        return '{0}/{1}/{2}.s.jpg'.format(settings.MEDIA_ROOT, path, basename)

    def save(self, update_thumbs=True, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(FeaturedArtistPicture, self).save(*args, **kwargs)
        logger.info(self.showcase_picture)
        if update_thumbs:
            process_images.apply_async(('fanart.models', 'FeaturedArtistPicture', self.id, 'small'), countdown=20)

    def __str__(self):
        return '{0}/{1}'.format(self.featured_artist.artist.username, self.showcase_picture.name)


class FeaturedPicture(models.Model):
    picture = models.ForeignKey('Picture', null=True, blank=True, on_delete=models.SET_NULL)
    date_featured = models.DateField()
    commentary = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)

    @property
    def commentary_parsed(self):
        return self.commentary.replace('A_NAME', self.picture.artist.username)

    def __str__(self):
        return self.picture.filename

    class Meta:
        ordering = ['-date_featured']


class ModNote(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    note = models.TextField(blank=True)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='modnotes_received', on_delete=models.SET_NULL)
    moderator = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['date_created']


class RevisionLog(models.Model):
    date_created = models.DateTimeField(null=True, blank=True, default=timezone.now)
    entry = models.TextField(blank=True)

    def is_recent(self):
        return (timezone.now() - self.date_created).days < settings.REVISION_LOG_RECENT_DAYS

#    def __str__(self):
#        return self.date_created


class BrowserStats(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    @property
    def user_agent_parsed(self):
        return parse_ua(self.user_agent)

    def __str__(self):
        return f'{self.date_created} w={self.width} h={self.height} {self.user}'


class ToolboxLink(models.Model):
    name = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    description = models.CharField(max_length=255, blank=True)
    order_by = models.IntegerField(blank=True, default=0)
