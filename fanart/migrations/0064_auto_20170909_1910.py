# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-09 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0063_vote'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contestentry',
            options={'verbose_name_plural': 'contest entries'},
        ),
        migrations.AlterModelOptions(
            name='socialmediaidentity',
            options={'verbose_name_plural': 'social media identities'},
        ),
        migrations.AddField(
            model_name='user',
            name='is_artist',
            field=models.BooleanField(default=False),
        ),
    ]
