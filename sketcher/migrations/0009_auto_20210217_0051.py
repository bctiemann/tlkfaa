# Generated by Django 2.2.14 on 2021-02-17 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sketcher', '0008_auto_20210217_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drawpile',
            name='status_message',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
