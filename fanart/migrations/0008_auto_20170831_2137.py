# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-31 21:37


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0007_auto_20170831_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='allow_shouts',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='allow_sketcher',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='auto_approve',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='banner_ext',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='user',
            name='banner_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='banner_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='banner_text_min',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='banner_text_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='birthday',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='user',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='commissions_open',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='dir_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='user',
            name='email_comments',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='email_pms',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='email_shouts',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='featured',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('', '(No response)')], max_length=10),
        ),
        migrations.AddField(
            model_name='user',
            name='is_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_paid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_upload',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='num_characters',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='num_favepics',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='num_faves',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='num_pictures',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='occupation',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_pic_ext',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_pic_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_birthdate',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_birthdate_age',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_coloring_cave',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='show_email',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='sketcher_ban_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='sketcher_banned',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='sketcher_banner_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='sort_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='user',
            name='suspension_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='website',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='zip_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='example_pic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fanart.Picture'),
        ),
    ]
