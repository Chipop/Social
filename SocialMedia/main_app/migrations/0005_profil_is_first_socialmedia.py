# Generated by Django 2.0.3 on 2018-05-04 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_auto_20180503_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='is_first_socialmedia',
            field=models.BooleanField(default=True),
        ),
    ]
