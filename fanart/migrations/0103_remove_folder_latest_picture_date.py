# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-29 13:44


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0102_auto_20171128_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='folder',
            name='latest_picture_date',
        ),
    ]
