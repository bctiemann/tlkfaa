# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-13 19:28


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0157_auto_20180711_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadedComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_orig', models.IntegerField(blank=True, db_index=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('date_edited', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_received', models.BooleanField(default=False)),
                ('hash', models.CharField(blank=True, max_length=36, null=True)),
                ('bulletin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Bulletin')),
                ('picture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Picture')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='fanart.ThreadedComment')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='picturecomment',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='picturecomment',
            name='reply_to',
        ),
        migrations.RemoveField(
            model_name='picturecomment',
            name='user',
        ),
        migrations.DeleteModel(
            name='PictureComment',
        ),
    ]