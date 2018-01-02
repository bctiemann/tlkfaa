# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-02 21:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=150)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('is_op', models.BooleanField(default=False)),
                ('is_mod', models.BooleanField(default=False)),
            ],
        ),
    ]
