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


def get_offers_path(instance, filename):
    return 'Artwork/offers/{0}.{1}'.format(instance.id, instance.extension)

def get_offers_thumb_path(instance, filename):
    return 'Artwork/offers/{0}.s.jpg'.format(instance.id)

def get_claims_path(instance, filename):
    return 'Artwork/claims/{0}.{1}'.format(instance.id, instance.extension)

def get_claims_thumb_path(instance, filename):
    return 'Artwork/claims/{0}.s.jpg'.format(instance.id)


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class Offer(models.Model):
    TYPE_CHOICES = (
        ('icon', 'Icon'),
        ('adoptable', 'Adoptable'),
    )

    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    artist = models.ForeignKey('fanart.User', null=True, blank=True)
    type = models.CharField(max_length=10, choices = TYPE_CHOICES, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    title = models.CharField(max_length=64, blank=True)
    comment = models.TextField(blank=True)
    filename = models.CharField(max_length=100, blank=True)
#    basename = models.CharField(max_length=100, blank=True)
#    extension = models.CharField(max_length=5, blank=True)
#    thumb_height = models.IntegerField(blank=True)
    picture = models.ImageField(max_length=255, storage=fanart_models.OverwriteStorage(), height_field='height', width_field='width', upload_to=get_offers_path, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    character = models.ForeignKey('fanart.Character', null=True, blank=True)
    adopted_by = models.ForeignKey('fanart.User', null=True, blank=True, related_name='trades_offered')
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)

    @property
    def open_claims(self):
        return self.claim_set.filter(date_fulfilled__isnull=True)

    @property
    def completed_claims(self):
        return self.claim_set.filter(date_fulfilled__isnull=False)

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def extension(self):
        return self.filename.split('.')[-1].lower()

    @property
    def thumbnail_path(self):
        if self.picture:
            path = ('/').join(self.picture.path.split('/')[:-1])
            return '{0}/{1}.s.jpg'.format(path, self.id)
        return os.path.join(settings.MEDIA_ROOT, 'Artwork', 'offers', '{0}.s.jpg'.format(self.id))

    @property
    def preview_path(self):
        if self.picture:
            path = ('/').join(self.picture.path.split('/')[:-1])
            return '{0}/{1}.p.jpg'.format(path, self.id)
        return os.path.join(settings.MEDIA_ROOT, 'Artwork', 'offers', '{0}.p.jpg'.format(self.id))

    @property
    def thumbnail_url(self):
        if os.path.exists(self.thumbnail_path):
            return '{0}Artwork/offers/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)
        return '{0}images/loading_spinner.gif'.format(settings.STATIC_URL)

    @property
    def preview_url(self):
        if os.path.exists(self.thumbnail_path):
            return '{0}Artwork/offers/{1}.p.jpg'.format(settings.MEDIA_URL, self.id)
        return '{0}images/loading_spinner.gif'.format(settings.STATIC_URL)

    @property
    def thumbnail_created(self):
        return os.path.exists(self.thumbnail_path)

    @property
    def preview_created(self):
        return os.path.exists(self.preview_path)

    @property
    def url(self):
        return '{0}Artwork/offers/{1}.{2}'.format(settings.MEDIA_URL, self.id, self.extension)

#    @property
#    def thumbnail_url(self):
#        return '{0}Artwork/offers/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)

    @property
    def thumb_width(self):
        return settings.THUMB_SIZE['offer']

    @property
    def thumb_height(self):
        if self.height and self.width:
            return int(self.height * settings.THUMB_SIZE['offer'] / self.width)
        return 0

    @property
    def thumb_height_x2(self):
        return self.thumb_height * 2

    def save(self, update_thumbs=True, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(Offer, self).save(*args, **kwargs)
        if update_thumbs:
            process_images.apply_async(('trading_tree.models', 'Offer', self.id, 'offer'), countdown=20)
            process_images.apply_async(('trading_tree.models', 'Offer', self.id, 'large'), countdown=20)

    def get_absolute_url(self):
        return reverse('offer', kwargs={'offer_id': self.id})

    def __unicode__(self):
        return '{0}'.format(self.id)


class Claim(models.Model):
    id_orig = models.IntegerField(null=True, blank=True, db_index=True)
    offer = models.ForeignKey('Offer', null=True, blank=True)
    user = models.ForeignKey('fanart.User', null=True, blank=True)
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
        return (self.offer.type == 'adoptable' and self.date_fulfilled != None and self.offer.is_active) or (self.offer.type == 'icon' and not self.date_fulfilled and self.filename)

    @property
    def basename(self):
        return '.'.join(self.filename.split('.')[:-1])

    @property
    def extension(self):
        return self.filename.split('.')[-1].lower()

    @property
    def thumbnail_path(self):
        if self.picture:
            path = ('/').join(self.picture.path.split('/')[:-1])
            return '{0}/{1}.s.jpg'.format(path, self.id)
        return os.path.join(settings.MEDIA_ROOT, 'Artwork', 'claims', '{0}.s.jpg'.format(self.id))

    @property
    def preview_path(self):
        if self.picture:
            path = ('/').join(self.picture.path.split('/')[:-1])
            return '{0}/{1}.p.jpg'.format(path, self.id)
        return os.path.join(settings.MEDIA_ROOT, 'Artwork', 'claims', '{0}.p.jpg'.format(self.id))

    @property
    def thumbnail_url(self):
        if os.path.exists(self.thumbnail_path):
            return '{0}Artwork/claims/{1}.s.jpg'.format(settings.MEDIA_URL, self.id)
        return '{0}images/loading_spinner.gif'.format(settings.STATIC_URL)

    @property
    def preview_url(self):
        if os.path.exists(self.preview_path):
            return '{0}Artwork/claims/{1}.p.jpg'.format(settings.MEDIA_URL, self.id)
        return '{0}images/loading_spinner.gif'.format(settings.STATIC_URL)

    @property
    def thumbnail_created(self):
        return os.path.exists(self.thumbnail_path)

    @property
    def preview_created(self):
        return os.path.exists(self.preview_path)

    @property
    def url(self):
        return '{0}Artwork/claims/{1}.{2}'.format(settings.MEDIA_URL, self.id, self.extension)

    def save(self, update_thumbs=True, *args, **kwargs):
        logger.info('Saving {0}, {1}'.format(self, update_thumbs))
        super(Claim, self).save(*args, **kwargs)
        if update_thumbs:
            process_images.apply_async(('trading_tree.models', 'Claim', self.id, 'small'), countdown=20)
            process_images.apply_async(('trading_tree.models', 'Claim', self.id, 'large'), countdown=20)

    def delete(self, *args, **kwargs):
        if self.offer.type == 'icon':
            os.remove(os.path.join(settings.MEDIA_ROOT, self.thumbnail_path))
            os.remove(self.thumbnail_path)
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, self.thumbnail_path))
                os.remove(self.thumbnail_path)
            except OSError:
                pass
        return super(Claim, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('upload-claim', kwargs={'claim_id': self.id})

    class Meta:
        ordering = ['date_posted']


