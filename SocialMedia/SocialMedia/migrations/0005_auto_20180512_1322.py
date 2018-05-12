# Generated by Django 2.0.5 on 2018-05-12 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMedia', '0004_remove_offreemploi_groupe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentaire',
            name='liked_by',
        ),
        migrations.RemoveField(
            model_name='statut',
            name='liked_by',
        ),
        migrations.AddField(
            model_name='commentaire',
            name='likes',
            field=models.ManyToManyField(to='SocialMedia.Like'),
        ),
        migrations.AddField(
            model_name='statut',
            name='likes',
            field=models.ManyToManyField(to='SocialMedia.Like'),
        ),
    ]