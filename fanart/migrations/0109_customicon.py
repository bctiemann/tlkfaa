# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-30 21:46


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0108_auto_20171130_0441'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomIcon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon_id', models.IntegerField(blank=True, null=True)),
                ('extension', models.CharField(blank=True, max_length=3)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
