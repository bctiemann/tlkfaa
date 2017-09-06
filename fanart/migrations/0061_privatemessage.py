# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-06 13:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0060_auto_20170906_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_sent', models.DateTimeField(blank=True, null=True)),
                ('subject', models.TextField(blank=True)),
                ('message', models.TextField(blank=True)),
                ('date_viewed', models.DateTimeField(blank=True, null=True)),
                ('date_replied', models.DateTimeField(blank=True, null=True)),
                ('deleted_by_sender', models.BooleanField(default=False)),
                ('deleted_by_recipient', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pms_received', to=settings.AUTH_USER_MODEL)),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.PrivateMessage')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pms_sent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
