# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-31 14:31


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0003_auto_20170831_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='folders_tree',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='h_size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_artist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='last_host',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='user',
            name='show_community_art_box',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_contests_box',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_favorite_artists_box',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_favorite_pictures_box',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_sketcher_box',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_tool_box',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='v_size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
