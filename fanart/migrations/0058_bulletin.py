# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-06 01:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0057_block'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bulletin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_posted', models.DateTimeField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False)),
                ('date_published', models.DateTimeField(blank=True, null=True)),
                ('title', models.TextField(blank=True)),
                ('bulletin', models.TextField(blank=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('show_email', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
