from __future__ import unicode_literals

from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    MALE = 'male'
    FEMALE = 'female'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        ('', '(No response)'),
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

    is_artist = models.BooleanField(default=False)

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
    banner_text_updated = models.DateTimeField(null=True)
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


class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, null=True, blank=True)


class Picture(models.Model):
    pass
