# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-24 00:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0136_auto_20171224_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='hash',
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
    ]