# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-06 04:48


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0154_auto_20180420_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='date_voted',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
