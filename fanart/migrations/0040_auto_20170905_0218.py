# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-05 02:18


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0039_picturecharacter_date_tagged'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picture',
            name='characters',
        ),
        migrations.AddField(
            model_name='picture',
            name='characters',
            field=models.ManyToManyField(through='fanart.PictureCharacter', to='fanart.Character'),
        ),
    ]
