# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-29 18:28
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0103_remove_folder_latest_picture_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftpicture',
            name='hash',
            field=models.UUIDField(blank=True, db_index=True, default=uuid.uuid4, null=True),
        ),
    ]