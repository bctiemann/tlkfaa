# Generated by Django 2.1.11 on 2019-08-31 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0163_auto_20190716_1746'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_featured', models.DateField()),
                ('commentary', models.TextField(blank=True)),
                ('picture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fanart.Picture')),
            ],
        ),
    ]
