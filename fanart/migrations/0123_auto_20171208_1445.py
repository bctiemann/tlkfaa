# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-08 14:45


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0122_auto_20171208_1357'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privatemessage',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='privatemessage',
            name='reply_to',
        ),
        migrations.RemoveField(
            model_name='privatemessage',
            name='sender',
        ),
        migrations.AlterModelOptions(
            name='block',
            options={'ordering': ['-date_blocked']},
        ),
        migrations.DeleteModel(
            name='PrivateMessage',
        ),
    ]
