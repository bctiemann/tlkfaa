# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-07 16:38


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0076_remove_tag_num_pictures'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='is_canon',
            field=models.BooleanField(default=False),
        ),
    ]
