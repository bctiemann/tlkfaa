# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-11 02:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0064_auto_20170909_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_artist',
        ),
    ]