# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-04 19:25


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0032_favorite_last_viewed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=255)),
                ('extension', models.CharField(blank=True, max_length=5)),
                ('type', models.CharField(blank=True, max_length=32)),
                ('is_movie', models.BooleanField(default=False)),
                ('has_thumb', models.BooleanField(default=False)),
                ('title', models.TextField(blank=True)),
                ('width', models.IntegerField(blank=True)),
                ('height', models.IntegerField(blank=True)),
                ('file_size', models.IntegerField(blank=True)),
                ('date_uploaded', models.DateTimeField(blank=True, null=True)),
                ('hash', models.CharField(blank=True, max_length=32)),
                ('notify_approval', models.BooleanField(default=False)),
                ('work_in_progress', models.BooleanField(default=False)),
                ('allow_comments', models.BooleanField(default=True)),
                ('reset_upload_date', models.BooleanField(default=False)),
                ('notify_replacement', models.BooleanField(default=False)),
                ('keywords', models.TextField(blank=True)),
                ('status', models.TextField(blank=True)),
                ('remote_host', models.CharField(blank=True, max_length=100)),
                ('remote_addr', models.CharField(blank=True, max_length=100)),
                ('user_agent', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('force_approve', models.BooleanField(default=False)),
                ('is_scanned', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_pictures', to=settings.AUTH_USER_MODEL)),
                ('artist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Folder')),
                ('replaces_picture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Picture')),
            ],
        ),
    ]
