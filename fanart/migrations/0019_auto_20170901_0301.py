# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-01 03:01


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0018_auto_20170901_0257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='artist_id_orig',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]
