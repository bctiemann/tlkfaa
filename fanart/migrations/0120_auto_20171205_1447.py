# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-05 14:47


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0119_auto_20171205_1325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oldcoloringbase',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='oldcoloringbase',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='oldcoloringpicture',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='oldcoloringpicture',
            name='base',
        ),
        migrations.DeleteModel(
            name='OldColoringBase',
        ),
        migrations.DeleteModel(
            name='OldColoringPicture',
        ),
    ]
