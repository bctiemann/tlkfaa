# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-17 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0158_auto_20190113_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='allow_replies',
            field=models.BooleanField(default=True),
        ),
    ]
