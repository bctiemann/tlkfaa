from __future__ import unicode_literals

from django.conf import settings
from django.db import models, connection
from django.db.models import Count, Avg
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

import uuid
import datetime

from fanart.utils import dictfetchall

import logging
logger = logging.getLogger(__name__)


def get_media_path(instance, filename):
    return '{0}/{1}'.format(instance.id, filename)

def get_image_thumb_small_path(instance, filename):
    return '{0}/thumb_small/{1}'.format(instance.id, filename)

def get_image_thumb_large_path(instance, filename):
    return '{0}/thumb_large/{1}'.format(instance.id, filename)


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class UserManager(BaseUserManager):

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

    dir_name = models.CharField(max_length=150, blank=True)
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

    objects = UserManager()

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
            print query
            cursor.execute(query, [self.id])
            result = dictfetchall(cursor)
        return result

    @property
    def favorite_pictures(self):
        return self.favorite_set.filter(artist__isnull=True, picture__isnull=False, character__isnull=True).prefetch_related('picture').order_by('-date_added')

    @property
    def recently_uploaded_pictures(self):
        three_days_ago = timezone.now() - datetime.timedelta(days=60)
        return self.picture_set.filter(is_public=True, date_deleted__isnull=True, date_uploaded__gt=three_days_ago).order_by('-date_uploaded')[0:10]

    @property
    def blocked_commenters(self):
        return [b.blocked_user for b in self.blocked_by.all()]

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.id, self.username, self.email)


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
    date_uploaded = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
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

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

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
        return reverse('picture', kwargs={'picture_id': self.picture.id})

    def __unicode__(self):
        return '{0} {1} on {2} by {3}'.format(self.id, self.user.username, self.picture, self.picture.artist.username)


class Shout(BaseComment):
    artist = models.ForeignKey('User', null=True, blank=True, related_name='shouts_received')

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

    @property
    def thumb_url(self):
        if not self.owner:
            return '{0}images/canon_characters/{1}.s.jpg'.format(settings.STATIC_URL, self.id)
        elif self.profile_picture:
            return '/Artwork/Artists/{0}/{1}.s.jpg'.format(self.owner.dir_name, self.profile_picture.basename)
        elif self.profile_coloring_picture:
            return '/Artwork/coloring/{0}.s.jpg'.format(self.profile_coloring_picture.id)
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
    date_added = models.DateTimeField(null=True, blank=True)
    last_viewed = models.DateTimeField(null=True, blank=True)

    objects = FavoriteManager()


class Pending(models.Model):
    artist = models.ForeignKey('User', null=True)
    folder = models.ForeignKey('Folder', null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    extension = models.CharField(max_length=5, blank=True)
    type = models.CharField(max_length=32, blank=True)
    is_movie = models.BooleanField(default=False)
    has_thumb = models.BooleanField(default=False)
    title = models.TextField(blank=True)
    width = models.IntegerField(blank=True)
    height = models.IntegerField(blank=True)
    file_size = models.IntegerField(blank=True)
    date_uploaded = models.DateTimeField(null=True, blank=True)
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


class ColoringBase(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    creator = models.ForeignKey('User', null=True, blank=True)
    picture = models.ForeignKey('Picture', null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    num_colored = models.IntegerField(null=True, blank=True)


class ColoringPicture(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('User', null=True, blank=True)
    base = models.ForeignKey('ColoringBase', null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    picture = models.ImageField(max_length=255, storage=OverwriteStorage(), height_field='height', width_field='width', upload_to=get_media_path, null=True, blank=True)
    extension = models.CharField(max_length=5, blank=True)
    width = models.IntegerField(blank=True)
    height = models.IntegerField(blank=True)
    thumb_height = models.IntegerField(blank=True)


class TradingOffer(models.Model):
    TYPE_CHOICES = (
        ('icon', 'Icon'),
        ('adoptable', 'Adoptable'),
    )

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('User', null=True, blank=True)
    type = models.CharField(max_length=10, choices = TYPE_CHOICES, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
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


class TradingClaim(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    offer = models.ForeignKey('TradingOffer', null=True, blank=True)
    user = models.ForeignKey('User', null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    reference_url = models.CharField(max_length=255, blank=True)
    date_fulfilled = models.DateTimeField(null=True, blank=True)
    filename = models.CharField(max_length=100, blank=True)
    basename = models.CharField(max_length=100, blank=True)
    extension = models.CharField(max_length=5, blank=True)
    date_uploaded = models.DateTimeField(null=True, blank=True)


class PictureCharacter(models.Model):
    picture = models.ForeignKey('Picture', null=True, blank=True)
    pending = models.ForeignKey('Pending', null=True, blank=True)
    character = models.ForeignKey('Character', null=True, blank=True)
    date_tagged = models.DateTimeField(null=True, blank=True)


class Tag(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    tag = models.CharField(max_length=255, blank=True)
    num_pictures = models.IntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    def __unicode__(self):
        return self.tag


class GiftPicture(models.Model):
    artist = models.ForeignKey('User', null=True, blank=True)
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
    date_added = models.DateTimeField(null=True, blank=True)


class ApprovalAccess(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    login = models.DateTimeField(null=True, blank=True)
    logout = models.DateTimeField(null=True, blank=True)


class AdminBlog(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)


class ArtistName(models.Model):
    artist = models.ForeignKey('User', null=True, blank=True)
    date_changed = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=32, blank=True)


class Block(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, related_name='blocked_by')
    blocked_user = models.ForeignKey('User', null=True, blank=True)
    date_blocked = models.DateTimeField(null=True, blank=True)


class Bulletin(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
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
    date_created = models.DateTimeField(null=True, blank=True)
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
        logger.info(self.date_end)
        logger.info(timezone.now())
        logger.info(self.date_end - timezone.now())
        return (self.date_end - timezone.now()).days

    def __unicode__(self):
        return self.title


class ContestEntry(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    contest = models.ForeignKey('Contest', null=True, blank=True)
    picture = models.ForeignKey('Picture', null=True, blank=True)
    date_entered = models.DateTimeField(null=True, blank=True)
    date_notified = models.DateTimeField(null=True, blank=True)

    @property
    def num_votes(self):
        return self.contestvote_set.count()

    class Meta:
        verbose_name_plural = 'contest entries'


class ContestVote(models.Model):
    entry = models.ForeignKey('ContestEntry', null=True, blank=True)
    user = models.ForeignKey('User', null=True, blank=True)
    date_voted = models.DateTimeField(null=True, blank=True)


class PrivateMessage(models.Model):
    sender = models.ForeignKey('User', null=True, blank=True, related_name='pms_sent')
    recipient = models.ForeignKey('User', null=True, blank=True, related_name='pms_received')
    date_sent = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey('PrivateMessage', null=True, blank=True)
    subject = models.TextField(blank=True)
    message = models.TextField(blank=True)
    date_viewed = models.DateTimeField(null=True, blank=True)
    date_replied = models.DateTimeField(null=True, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)


class SpecialFeature(models.Model):
    keyword = models.CharField(max_length=32, blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)


class Vote(models.Model):
    voter = models.ForeignKey('User', null=True, blank=True, related_name='votes_cast')
    artist = models.ForeignKey('User', null=True, blank=True, related_name='votes_received')
