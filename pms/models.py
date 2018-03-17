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


class PrivateMessage(models.Model):
    sender = models.ForeignKey('fanart.User', null=True, blank=True, related_name='pms_sent')
    recipient = models.ForeignKey('fanart.User', null=True, blank=True, related_name='pms_received')
#    sender = models.ForeignKey('fanart.User', related_name='pms_sent')
#    recipient = models.ForeignKey('fanart.User', related_name='pms_received')
    date_sent = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reply_to = models.ForeignKey('PrivateMessage', null=True, blank=True)
    root_pm = models.ForeignKey('PrivateMessage', null=True, blank=True, related_name='thread_pms')
    subject = models.TextField(blank=True)
    message = models.TextField(blank=True)
    date_viewed = models.DateTimeField(null=True, blank=True)
    date_replied = models.DateTimeField(null=True, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)

    @property
    def quoted_message(self):
        return '\n\n\n[quote]\n{0}\n[/quote]'.format(self.message)

    @property
    def thread(self):
        return self.root_pm.thread_pms.order_by('-date_sent')

    @property
    def is_latest_reply(self):
        return not self.thread.filter(reply_to=self).exists()

    class Meta:
        ordering = ['-date_sent']

