# -*- coding: utf-8 -*-


from django.db import models


class ActiveUser(models.Model):
    name = models.CharField(max_length=150, blank=True, default='')
    ip = models.GenericIPAddressField(null=True, blank=True)
    is_op = models.BooleanField(default=False)
    is_mod = models.BooleanField(default=False)


class Ban(models.Model):
    user = models.ForeignKey('fanart.User', on_delete=models.CASCADE)
    date_banned = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    banned_by = models.ForeignKey('fanart.user', null=True, blank=True, related_name='sketcher_banned_users', on_delete=models.SET_NULL)
    ban_reason = models.TextField(blank=True, default='')
