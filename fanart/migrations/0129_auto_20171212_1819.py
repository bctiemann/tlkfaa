# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-12 18:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0128_featuredartist_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='featuredartist',
            options={'ordering': ['-date_featured']},
        ),
        migrations.RenameField(
            model_name='featuredartist',
            old_name='is_active',
            new_name='is_published',
        ),
    ]