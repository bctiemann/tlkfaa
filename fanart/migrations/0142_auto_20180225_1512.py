# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-25 15:12


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0141_auto_20180102_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='pending',
            name='locked_for_publish',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, verbose_name='username'),
        ),
    ]
