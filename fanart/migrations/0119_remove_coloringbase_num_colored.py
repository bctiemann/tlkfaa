# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-04 03:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0118_auto_20171204_0247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coloringbase',
            name='num_colored',
        ),
    ]
