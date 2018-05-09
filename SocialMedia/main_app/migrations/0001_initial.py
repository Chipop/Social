# Generated by Django 2.0.5 on 2018-05-09 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=300)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Entreprise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=300)),
                ('activite', models.CharField(max_length=255)),
                ('secteurActivite', models.CharField(choices=[('Publique', 'Publique'), ('Prive', 'Privé')], max_length=255)),
                ('capitale', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pays', models.CharField(max_length=255)),
                ('ville', models.CharField(max_length=255)),
                ('codePostal', models.IntegerField()),
                ('tel', models.IntegerField()),
                ('civilite', models.CharField(max_length=255)),
                ('adresse_profile', models.CharField(max_length=255)),
                ('logo', models.FileField(null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='', upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('website', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('facebook', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('youtube', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('instagram', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('linkedin', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('twitter', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('tel', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('ville', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('pays', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('fonction', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('service', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('token_email', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('token_email_expiration', models.DateTimeField(blank=True, null=True)),
                ('civilité', models.CharField(max_length=255)),
                ('adresse_profile', models.CharField(max_length=255)),
                ('is_first_socialmedia', models.BooleanField(default=True)),
                ('genre', models.CharField(choices=[('homme', 'Homme'), ('femme', 'Femme')], default='homme', max_length=20, verbose_name='Genre')),
                ('entreprise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.Entreprise')),
                ('photo_couverture', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photo_cover', to='main_app.Image')),
                ('photo_profil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profil_photo', to='main_app.Image')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TypeEntreprise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('publique', 'publique'), ('prive', 'prive')], max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='entreprise',
            name='typeEntreprise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.TypeEntreprise'),
        ),
    ]
