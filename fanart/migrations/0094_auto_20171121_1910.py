# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-21 19:10


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0093_auto_20171121_1901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistname',
            name='name',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
