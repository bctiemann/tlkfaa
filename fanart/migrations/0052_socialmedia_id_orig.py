# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-05 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0051_socialmedia_socialmediaidentity'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmedia',
            name='id_orig',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]
