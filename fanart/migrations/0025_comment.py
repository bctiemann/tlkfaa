# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-01 21:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0024_auto_20170901_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_orig', models.IntegerField(blank=True, db_index=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('date_posted', models.DateTimeField()),
                ('date_edited', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_received', models.BooleanField(default=False)),
                ('hash', models.CharField(blank=True, max_length=36, null=True)),
                ('picture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fanart.Picture')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='fanart.Comment')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
