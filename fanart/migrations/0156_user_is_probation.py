# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-07-11 12:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0155_vote_date_voted'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_probation',
            field=models.BooleanField(default=False),
        ),
    ]