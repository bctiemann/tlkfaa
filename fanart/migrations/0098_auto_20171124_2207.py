# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-24 22:07


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0097_auto_20171124_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pending',
            name='file_size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
