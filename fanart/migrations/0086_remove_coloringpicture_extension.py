# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 18:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0085_coloringpicture_filename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coloringpicture',
            name='extension',
        ),
    ]