# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-02 21:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0140_auto_20171226_1611'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ['-date_added']},
        ),
    ]