# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-24 00:02


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0135_auto_20171222_1426'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pending',
            old_name='type',
            new_name='mime_type',
        ),
    ]
