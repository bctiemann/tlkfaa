# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-01 01:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0012_auto_20170901_0142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='user',
        ),
        migrations.DeleteModel(
            name='Artist',
        ),
    ]
