from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Image(models.Model):
    image = models.ImageField(default="")

    def __str__(self):
        return str(self.image)


class TypeEntreprise(models.Model):
   type = models.CharField(max_length=255)


class Entreprise(models.Model):
    types = (('petite', 'Petite entreprise'), ('grande', 'Grande entreprise'), ('tres petite', 'Très petite entreprise'), ('entreprise intermediaire', 'Entreprise de taille intermediaire'))
    secteurs = (('Publique', 'Publique'), ('Prive', 'Privé'))
    nom = models.CharField(max_length=300, null=False, blank=False,unique=True)
    activite = models.CharField(max_length=255, null=False, blank=False)
    secteurActivite = models.CharField(choices=secteurs, null=False, blank=False, max_length=255)
    capitale = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=10)
    pays = models.CharField(max_length=255, blank=False, null=False)
    ville = models.CharField(max_length=255, null=False, blank=False)
    codePostal = models.IntegerField()
    tel = models.IntegerField()
    typeEntreprise = models.CharField(max_length=255, choices=types)
    civilite = models.CharField(max_length=255, blank=False, null=False)
    adresse_profile = models.CharField(max_length=255, blank=False, null=False)
    logo = models.FileField(upload_to="", null=True)
    a_propos = models.CharField(max_length=255, blank=False, null=False)
    siege_social = models.CharField(max_length=255, blank=False, null=False)
    annee_creation = models.IntegerField()
    specialisation = models.CharField(max_length=255, blank=False, null=False)

    @staticmethod
    def noms_entreprises():
        noms_entreprises = ""
        for entreprise in Entreprise.objects.all():
            noms_entreprises += entreprise.nom + ","
        return noms_entreprises[:-1]

    def __str__(self):
        return self.nom


class Profil(models.Model):
    GENRE_CHOICES = [('homme', 'Homme'),
                     ('femme', 'Femme')]
    date_naissance = models.DateField(null=True, blank=True)
    website = models.CharField(max_length=300, default="", null=True, blank=True)
    entreprise = models.ForeignKey(Entreprise, blank=True, null=True, on_delete=models.CASCADE)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    photo_profil = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name="profil_photo")
    photo_couverture = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE,
                                         related_name="photo_cover")
    facebook = models.CharField(max_length=300, blank=True, null=True, default="")
    youtube = models.CharField(max_length=300, blank=True, null=True, default="")
    instagram = models.CharField(max_length=300, blank=True, null=True, default="")
    linkedin = models.CharField(max_length=300, blank=True, null=True, default="")
    twitter = models.CharField(max_length=300, blank=True, null=True, default="")
    tel = models.CharField(max_length=300, blank=True, null=True, default="")
    ville = models.CharField(max_length=300, blank=True, null=True, default="")
    pays = models.CharField(max_length=300, blank=True, null=True, default="")
    fonction = models.CharField(max_length=300, blank=True, null=True, default="")
    service = models.CharField(max_length=300, blank=True, null=True, default="")
    token_email = models.CharField(max_length=300, blank=True, null=True, default="")
    token_email_expiration = models.DateTimeField(blank=True, null=True)
    civilité = models.CharField(max_length=255, blank=False, null=False)
    adresse_profile = models.CharField(max_length=255, blank=False, null=False)
    is_first_socialmedia = models.BooleanField(default=True)
    genre = models.CharField(u'Genre', choices=GENRE_CHOICES, blank=False, default='homme', max_length=20)
    formation_profil = models.ForeignKey('SocialMedia.Formation', on_delete=models.CASCADE, blank=True, null=True,
                                         related_name="formation_profil")
    experience_profil = models.ForeignKey('SocialMedia.Experience', on_delete=models.CASCADE, blank=True, null=True,
                                          related_name="experience_profil")
    resume = models.CharField(max_length=300, blank=True, null=True, default="")

    def __str__(self):
        return self.user.username


class Contact(models.Model):
    full_name = models.CharField(max_length=300)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.full_name
