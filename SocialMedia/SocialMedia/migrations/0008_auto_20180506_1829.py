# Generated by Django 2.0.3 on 2018-05-06 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_auto_20180506_1829'),
        ('SocialMedia', '0007_auto_20180506_0314'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionbenevole',
            name='profil',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main_app.Profil'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='experience',
            name='profil',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main_app.Profil'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formation',
            name='profil',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main_app.Profil'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formation',
            name='titre_formation',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='actionbenevole',
            name='cause',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='actionbenevole',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='actionbenevole',
            name='organisme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialMedia.Organisme'),
        ),
        migrations.AlterField(
            model_name='actionbenevole',
            name='poste',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialMedia.Poste'),
        ),
        migrations.AlterField(
            model_name='experience',
            name='date_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='entreprise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.Entreprise'),
        ),
        migrations.AlterField(
            model_name='experience',
            name='poste',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialMedia.Poste'),
        ),
        migrations.AlterField(
            model_name='formation',
            name='activite_et_associations',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='formation',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='formation',
            name='domaine',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='formation',
            name='ecole',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SocialMedia.Ecole'),
        ),
        migrations.AlterField(
            model_name='formation',
            name='resultat_obtenu',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
