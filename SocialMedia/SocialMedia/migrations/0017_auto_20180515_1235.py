# Generated by Django 2.0.5 on 2018-05-15 12:35

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMedia', '0016_auto_20180514_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statut',
            name='contenu_statut',
            field=tinymce.models.HTMLField(),
        ),
    ]
