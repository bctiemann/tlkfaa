# Generated by Django 2.2.10 on 2020-05-17 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0168_auto_20200517_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pronouns',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('non-binary', 'Non-binary'), ('', '(No response)')], max_length=10),
        ),
    ]
