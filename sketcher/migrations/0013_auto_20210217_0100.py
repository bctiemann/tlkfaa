# Generated by Django 2.2.14 on 2021-02-17 01:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sketcher', '0012_drawpile_drawpile_site_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='drawpile',
            old_name='drawpile_site_url',
            new_name='download_url',
        ),
    ]
