# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-31 01:21


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sketcher', '0002_ban'),
    ]

    operations = [
        migrations.AddField(
            model_name='ban',
            name='ban_reason',
            field=models.TextField(blank=True, default=''),
        ),
    ]
