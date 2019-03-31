# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-05 02:51


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0040_auto_20170905_0218'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=255)),
                ('num_pictures', models.IntegerField(blank=True, null=True)),
                ('is_visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='picture',
            name='tags',
            field=models.ManyToManyField(to='fanart.Tag'),
        ),
    ]
