from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, null=True, blank=True)
