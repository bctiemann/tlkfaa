# Generated by Django 2.2.10 on 2020-05-17 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0166_auto_20200217_2338'),
    ]

    operations = [
        migrations.AddField(
            model_name='shout',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='fanart.Shout'),
        ),
    ]
