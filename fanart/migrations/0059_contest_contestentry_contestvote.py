# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-06 02:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0058_bulletin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('global', 'Global'), ('personal', 'Personal')], max_length=16)),
                ('title', models.CharField(blank=True, max_length=64)),
                ('description', models.TextField(blank=True)),
                ('rules', models.TextField(blank=True)),
                ('date_created', models.DateTimeField(blank=True, null=True)),
                ('date_start', models.DateTimeField(blank=True, null=True)),
                ('date_end', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('allow_multiple_entries', models.BooleanField(default=False)),
                ('allow_anonymous_entries', models.BooleanField(default=False)),
                ('allow_voting', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContestEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_entered', models.DateTimeField(blank=True, null=True)),
                ('date_notified', models.DateTimeField(blank=True, null=True)),
                ('contest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Contest')),
                ('picture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Picture')),
            ],
        ),
        migrations.CreateModel(
            name='ContestVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_voted', models.DateTimeField(blank=True, null=True)),
                ('entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.ContestEntry')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
