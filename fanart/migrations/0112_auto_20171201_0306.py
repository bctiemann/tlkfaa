# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-01 03:06


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0111_banner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='banner',
            name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='banner_ext',
        ),
        migrations.RemoveField(
            model_name='user',
            name='banner_id',
        ),
        migrations.AddField(
            model_name='user',
            name='banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Banner'),
        ),
    ]
