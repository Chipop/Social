# Generated by Django 2.0.5 on 2018-05-10 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMedia', '0002_auto_20180510_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='offreemploi',
            name='groupe',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='SocialMedia.Groupe'),
            preserve_default=False,
        ),
    ]
