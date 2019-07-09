# Generated by Django 2.1.9 on 2019-07-09 01:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pms', '0003_privatemessage_root_pm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatemessage',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pms.PrivateMessage'),
        ),
        migrations.AlterField(
            model_name='privatemessage',
            name='root_pm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='thread_pms', to='pms.PrivateMessage'),
        ),
    ]
