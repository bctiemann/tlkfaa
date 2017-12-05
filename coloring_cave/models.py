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

from fanart import models as fanart_models
from fanart.utils import dictfetchall
from fanart.tasks import process_images

import logging
logger = logging.getLogger(__name__)

THREE = 90


def get_coloring_path(instance, filename):
    return 'Artwork/coloring/{0}.{1}'.format(instance.id, instance.extension)

def get_coloring_thumb_path(instance, filename):
    return 'Artwork/coloring/{0}.s.jpg'.format(instance.id)


#class OverwriteStorage(FileSystemStorage):
#
#    def get_available_name(self, name, max_length=None):
#        self.delete(name)
#        return name


class Base(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    creator = models.ForeignKey('fanart.User', null=True, blank=True, related_name='coloringbase_set')
    picture = models.ForeignKey('fanart.Picture', null=True, blank=True, related_name='coloringbase_set')
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    num_colored = models.IntegerField(null=True, blank=True, default=0)

#    @property
#    def num_colored(self):
#        return self.coloringpicture_set.count()

    @property
    def thumbnail_url(self):
        return '{0}Artwork/Artists/{1}/{2}.s.jpg'.format(settings.MEDIA_URL, self.picture.artist.dir_name, self.picture.basename)

    @property
    def thumb_width(self):
        return settings.THUMB_SIZE['small']

    @property
    def thumb_height(self):
        if self.picture:
            return self.picture.thumb_height
#            return int(self.picture.height * settings.THUMB_SIZE['small'] / self.width)
        return 0

    @property
    def thumb_height_x2(self):
        return self.thumb_height * 2

    def refresh_num_colored(self):
        self.num_colored = self.coloringpicture_set.count()
        self.save()

    def get_absolute_url(self):
        return reverse('coloring-cave', kwargs={'coloring_base_id': self.id})


class ColoringPicture(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('fanart.User', null=True, blank=True)
    base = models.ForeignKey('Base', null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    comment = models.TextField(blank=True)
    filename = models.CharField(max_length=100, blank=True)
    picture = models.ImageField(max_length=255, storage=fanart_models.OverwriteStorage(), height_field='height', width_field='width', upload_to=get_coloring_path, null=True, blank=True)
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
    def preview_url(self):
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
            process_images.apply_async(('coloring_cave.models', 'ColoringPicture', self.id, 'small'), countdown=20)

    def delete(self, *args, **kwargs):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.picture.name))
            os.remove(os.path.join(settings.MEDIA_ROOT, self.thumbnail_path))
        except OSError:
            pass

        for character in fanart_models.Character.objects.filter(profile_coloring_picture=self):
            character.profile_coloring_picture = None
            character.save()

        self.base.refresh_num_colored()

        super(ColoringPicture, self).delete(*args, **kwargs)


