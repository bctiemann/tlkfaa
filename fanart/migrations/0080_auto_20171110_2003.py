# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-10 20:03
from __future__ import unicode_literals

from django.db import migrations, models
import fanart.models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0079_character_num_pictures'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', fanart.models.FanartUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='tradingclaim',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='tradingoffer',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]