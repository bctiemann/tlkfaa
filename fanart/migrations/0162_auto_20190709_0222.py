# Generated by Django 2.1.9 on 2019-07-09 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0161_auto_20190709_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pending',
            name='height',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='pending',
            name='width',
            field=models.IntegerField(default=0),
        ),
    ]
