# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-17 21:42


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0090_auto_20171117_0148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='giftpicture',
            old_name='artist',
            new_name='sender',
        ),
    ]
