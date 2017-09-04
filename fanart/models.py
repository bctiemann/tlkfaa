from __future__ import unicode_literals

from django.db import models
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import ugettext_lazy as _


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
    is_active = models.BooleanField(default=True)
    is_enabled = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
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
    characters = models.CharField(max_length=50, blank=True)
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
    needs_poster = models.BooleanField(default=False)

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
    date_posted = models.DateTimeField()
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

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.id, self.name, self.owner.username)


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


class Favorite(models.Model):
    user = models.ForeignKey('User', null=True, blank=True)
    artist = models.ForeignKey('User', null=True, blank=True, related_name='fans')
    picture = models.ForeignKey('Picture', null=True, blank=True, related_name='fans')
    character = models.ForeignKey('Character', null=True, blank=True, related_name='fans')
    is_visible = models.BooleanField(default=True)
    date_added = models.DateTimeField(null=True, blank=True)
    last_viewed = models.DateTimeField(null=True, blank=True)
