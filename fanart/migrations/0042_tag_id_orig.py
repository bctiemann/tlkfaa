# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-05 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0041_auto_20170905_0251'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='id_orig',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]
