# Generated by Django 2.1.9 on 2019-07-09 01:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sketcher', '0004_auto_20180331_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ban',
            name='banned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sketcher_banned_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
