# Generated by Django 2.0.3 on 2018-05-13 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_auto_20180513_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='resume',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
    ]