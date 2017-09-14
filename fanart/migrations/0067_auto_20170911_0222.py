# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-11 02:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0066_auto_20170911_0219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_enabled',
        ),
        migrations.AddField(
            model_name='user',
            name='is_artist',
            field=models.BooleanField(default=True, help_text='Controls whether user has a visible artist page and has access to artist modules in ArtManager, or simply a Profile for following others.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Controls whether user is allowed to log in. Uncheck this to disable accounts.'),
        ),
    ]