# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-10 12:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0147_auto_20180306_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevisionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('comment', models.TextField(blank=True)),
            ],
        ),
    ]