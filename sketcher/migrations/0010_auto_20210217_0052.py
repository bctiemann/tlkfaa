# Generated by Django 2.2.14 on 2021-02-17 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sketcher', '0009_auto_20210217_0051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drawpile',
            name='last_checked_at',
            field=models.DateTimeField(blank=True),
        ),
    ]
