# Generated by Django 2.0.5 on 2018-05-14 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMedia', '0014_auto_20180514_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statut',
            name='likes',
            field=models.ManyToManyField(blank=True, null=True, to='main_app.Profil'),
        ),
    ]