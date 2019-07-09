# Generated by Django 2.1.9 on 2019-07-09 01:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coloring_cave', '0002_auto_20171205_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='base',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coloringbase_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='base',
            name='picture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coloringbase_set', to='fanart.Picture'),
        ),
        migrations.AlterField(
            model_name='coloringpicture',
            name='artist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='coloringpicture',
            name='base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='coloring_cave.Base'),
        ),
    ]
