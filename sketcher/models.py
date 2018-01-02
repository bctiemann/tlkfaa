# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class ActiveUser(models.Model):
    name = models.CharField(max_length=150, blank=True, default='')
    ip = models.GenericIPAddressField(null=True, blank=True)
    is_op = models.BooleanField(default=False)
    is_mod = models.BooleanField(default=False)
