# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-31 21:48


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0009_user_allow_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='sketcher_banner_by',
            new_name='sketcher_banned_by',
        ),
    ]
