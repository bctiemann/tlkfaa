# Generated by Django 2.2.14 on 2021-02-17 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sketcher', '0006_drawpile'),
    ]

    operations = [
        migrations.AddField(
            model_name='drawpile',
            name='admin_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]