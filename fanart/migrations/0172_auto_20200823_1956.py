# Generated by Django 2.2.14 on 2020-08-23 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0171_browserstats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pending',
            name='height',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='pending',
            name='width',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
