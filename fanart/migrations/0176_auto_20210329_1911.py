# Generated by Django 2.2.18 on 2021-03-29 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0175_auto_20210329_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_active',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]