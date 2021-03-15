# -*- coding: utf-8 -*-


from django.db import models


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
