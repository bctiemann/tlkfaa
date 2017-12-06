# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-05 15:27
from __future__ import unicode_literals

import coloring_cave.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import fanart.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fanart', '0120_auto_20171205_1447'),
        ('coloring_cave', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Base',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_orig', models.IntegerField(blank=True, db_index=True, null=True)),
                ('date_posted', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_visible', models.BooleanField(default=True)),
                ('num_colored', models.IntegerField(blank=True, default=0, null=True)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coloringbase_set', to=settings.AUTH_USER_MODEL)),
                ('picture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coloringbase_set', to='fanart.Picture')),
            ],
        ),
        migrations.RemoveField(
            model_name='coloringbase',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='coloringbase',
            name='picture',
        ),
        migrations.AlterField(
            model_name='coloringpicture',
            name='base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coloring_cave.Base'),
        ),
        migrations.AlterField(
            model_name='coloringpicture',
            name='picture',
            field=models.ImageField(blank=True, height_field='height', max_length=255, null=True, storage=fanart.models.OverwriteStorage(), upload_to=coloring_cave.models.get_coloring_path, width_field='width'),
        ),
        migrations.DeleteModel(
            name='ColoringBase',
        ),
    ]