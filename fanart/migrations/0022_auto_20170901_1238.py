# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-01 12:38


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0021_auto_20170901_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='id_orig',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
