# -*- coding: utf-8 -*-

import secrets

from django.db import models
from django.utils import timezone
from datetime import timedelta


class Drawpile(models.Model):
    last_checked_at = models.DateTimeField(null=True, blank=True)
    is_running = models.BooleanField(default=False)
    status_message = models.CharField(max_length=255, blank=True)
    host = models.CharField(max_length=100)
    port = models.IntegerField()
    admin_url = models.URLField()
    download_url = models.URLField()

    @property
    def active_users(self):
        return self.activeuser_set.all()


class ActiveUser(models.Model):
    drawpile = models.ForeignKey('sketcher.Drawpile', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, default='')
    ip = models.GenericIPAddressField(null=True, blank=True)
    is_op = models.BooleanField(default=False)
    is_mod = models.BooleanField(default=False)


class Ban(models.Model):
    drawpile = models.ForeignKey('sketcher.Drawpile', null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey('fanart.User', on_delete=models.CASCADE)
    date_banned = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    banned_by = models.ForeignKey('fanart.user', null=True, blank=True, related_name='sketcher_banned_users', on_delete=models.SET_NULL)
    ban_reason = models.TextField(blank=True, default='')


class SketcherAccessToken(models.Model):
    """
    Short-lived, single-use token minted for a logged-in TLKFAA user so the
    standalone Sketcher (Java) client can authenticate against this site
    without the desktop app ever seeing the user's Django session cookie.

    Unrelated to the Drawpile/Ban models above, despite living in the same
    app - those track the older, separate Drawpile integration.
    """
    TOKEN_LIFETIME = timedelta(minutes=5)

    user = models.ForeignKey('fanart.User', on_delete=models.CASCADE, related_name='sketcher_access_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue_for(cls, user):
        return cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + cls.TOKEN_LIFETIME,
        )

    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])

    def __str__(self):
        return f'{self.user.username} ({self.created_at:%Y-%m-%d %H:%M})'
