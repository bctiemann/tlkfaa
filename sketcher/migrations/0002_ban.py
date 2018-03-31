# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-31 01:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sketcher', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_banned', models.DateTimeField(auto_now_add=True, null=True)),
                ('banned_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sketcher_banned_users', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
