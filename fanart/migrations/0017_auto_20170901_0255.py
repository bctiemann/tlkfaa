# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-01 02:55


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0016_auto_20170901_0209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='folder',
            name='parent_folder_id',
        ),
        migrations.AddField(
            model_name='folder',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Folder'),
        ),
    ]
