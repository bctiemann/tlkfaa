# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-02 18:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0025_picturecomment_shout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shout',
            name='reply_to',
        ),
    ]
