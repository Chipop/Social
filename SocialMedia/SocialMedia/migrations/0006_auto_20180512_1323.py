# Generated by Django 2.0.5 on 2018-05-12 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMedia', '0005_auto_20180512_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statut',
            name='likes',
            field=models.ManyToManyField(blank=True, null=True, to='SocialMedia.Like'),
        ),
    ]