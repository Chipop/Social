# Generated by Django 2.0.3 on 2018-05-03 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_auto_20180503_1805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profil',
            name='is_first_marketplace',
        ),
        migrations.RemoveField(
            model_name='profil',
            name='is_first_reseausocial',
        ),
    ]