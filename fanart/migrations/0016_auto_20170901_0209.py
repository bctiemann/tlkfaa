# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-01 02:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0015_user_id_orig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='banner_text_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
