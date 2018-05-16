# Generated by Django 2.0.3 on 2018-05-15 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_profil_resume'),
    ]

    operations = [
        migrations.AddField(
            model_name='entreprise',
            name='a_propos',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entreprise',
            name='annee_creation',
            field=models.IntegerField(default=1990),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entreprise',
            name='siege_social',
            field=models.CharField(default='casablanca', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entreprise',
            name='specialisation',
            field=models.CharField(default='Informatique', max_length=255),
            preserve_default=False,
        ),
    ]
