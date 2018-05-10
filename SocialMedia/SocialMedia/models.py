from django.db import models
from django.contrib.auth.models import User
import os.path



# Create your models here.

class Notification(models.Model):
    url = models.URLField(max_length=500)
    message = models.CharField(max_length=1000)
    statut = models.BooleanField(default=False)
    read_date = models.DateTimeField(default=False)
    profil_to_notify = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)


class Groupe(models.Model):
    statuts = (('publique', 'publique'), ('prive', 'privé'))
    nom = models.CharField(max_length=255)
    date_creation = models.DateField()
    statut_groupe = models.CharField(choices=statuts, max_length=255, null=False, blank=False)
    have_image = models.BooleanField(default=False)
    description = models.TextField(default="")
    photo_profil = models.OneToOneField('main_app.Image', on_delete=models.CASCADE, related_name="groupe_photo")
    photo_couverture = models.OneToOneField('main_app.Image', on_delete=models.CASCADE, related_name="profil_cover")
    admins = models.ManyToManyField('main_app.Profil', related_name="admin")
    moderators = models.ManyToManyField('main_app.Profil', related_name="moderateur")
    creator = models.OneToOneField('main_app.Profil', on_delete=models.CASCADE, related_name="createur")
    adherents = models.ManyToManyField('main_app.Profil', related_name="adherent")

    def __str__(self):
        return "Groupe: " + self.nom + "\b\bCree Par: " + self.creator.user.username


class DemandeGroupe(models.Model):
    emetteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    groupe_recepteur = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    reponse = models.BooleanField()

    def __str__(self):
        return self.emetteur.user.username + " à demandé de rejoidre le groupe " + self.groupe_recepteur.nom


class Like(models.Model):
    user = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE,related_name="like_user")
    like_date_time = models.DateTimeField(auto_now_add=True)


class Statut(models.Model):
    date_statut = models.DateTimeField()
    contenu_statut = models.CharField(max_length=6000)
    is_group_statut = models.BooleanField(default=False)
    is_profil_statut = models.BooleanField(default=False)
    publisher = models.OneToOneField('main_app.Profil', on_delete=models.CASCADE, related_name="pub")
    mur_profil = models.OneToOneField('main_app.Profil', on_delete=models.CASCADE, null=True, blank=True,
                                      related_name="statut_mur_profil")
    mur_groupe = models.OneToOneField(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    liked_by = models.ManyToManyField('main_app.Profil',related_name="statut_liked_by")


class Commentaire(models.Model):
    comment = models.CharField(null=False, blank=False, max_length=6000)
    date_commentaire = models.DateField()
    statut = models.OneToOneField(Statut, on_delete=models.CASCADE)
    user = models.OneToOneField('main_app.Profil', on_delete=models.CASCADE, related_name="commented_user")
    have_image = models.BooleanField(default=False)
    image = models.OneToOneField('main_app.Image', on_delete=models.CASCADE)
    liked_by = models.ManyToManyField('main_app.Profil')


class DemandeAmi(models.Model):
    demandes = ((0, 'En Cours'), (1, 'Acceptée'), (2, 'Refusée'), (3, 'Bloquée'))
    emetteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="sender")
    recepteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="receiver")
    statut = models.IntegerField(null=False, blank=False, choices=demandes)

    def __str__(self):
        return self.demandes[self.statut][1]


class Suivie(models.Model):
    follower = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="suiveur")
    followed_profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="suive")

    class Meta:
        unique_together = ('follower', 'followed_profil',)


class Conversation(models.Model):
    start_date = models.DateTimeField(blank=False)
    participants = models.ManyToManyField(User)

    def __str__(self):
        show = ""
        for user in self.participants.all():
            show += " || Participant Username: " + user.username
        return show


class Responseconversation(models.Model):
    message = models.CharField(max_length=6000)
    message_date = models.DateTimeField(blank=False)
    is_image = models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    image = models.ForeignKey('main_app.Image', on_delete=models.CASCADE, blank=True, null=True)
    user_responsed = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return "Response Of: " + self.user_responsed.username


VALID_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
]


def generate_path(instance, filename):
    extension = os.path.splitext(filename)[1][1:]
    if extension in VALID_IMAGE_EXTENSIONS:
        path = 'SocialMedia/Image/'
    else:
        path = 'SocialMedia/Fichier/'

    return os.path.join(path, instance.fichier.name)


class Album(models.Model):
    nom = models.CharField(max_length=300)
    date_creation = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class ReseauSocialFile(models.Model):
    fichier = models.FileField(upload_to=generate_path)
    date_telechargement = models.DateTimeField()
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    likes = models.ManyToManyField(Like)
    comment = models.ManyToManyField(Commentaire)

    def __str__(self):
        return self.fichier.name


class Poste(models.Model):
    nom_poste = models.CharField(max_length=300)


class OffreEmploi(models.Model):
    TYPES_EMPLOI = (('plein', 'Plein temps'), ('partiel', 'Temps partiel'))
    tel = models.IntegerField()
    email = models.EmailField()
    pays = models.CharField(max_length=300)
    ville = models.CharField(max_length=300)
    diplome_requis = models.CharField(max_length=300)
    type_contrat = models.CharField(max_length=300)
    description_poste = models.TextField()
    profil_recherche = models.TextField()
    presentation_entreprise = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    type_emploi = models.CharField(max_length=300, choices=TYPES_EMPLOI)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE,
                              related_name="poste_recherche")
    nom_poste = models.CharField(max_length=300)
    en_cours = models.BooleanField()
    entreprise = models.ForeignKey('main_app.Entreprise', on_delete=models.CASCADE)
    profil_publicateur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE,
                                           related_name="profil_publicateur")
    profil_postulants = models.ManyToManyField('main_app.Profil', related_name="profil_postulants" ,blank=True)



class Experience(models.Model):
    entreprise = models.ForeignKey('main_app.Entreprise', on_delete=models.CASCADE, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=300)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, null=True, blank=True)
    nom_poste = models.CharField(max_length=300)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    actuel = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)


class Ecole(models.Model):
    nom = models.CharField(max_length=300)
    logo = models.ImageField(upload_to="SocialMedia/Image/")


class Formation(models.Model):
    titre_formation = models.CharField(max_length=300)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, null=True, blank=True)
    nom_ecole = models.CharField(max_length=300)
    domaine = models.CharField(max_length=300, null=True, blank=True)
    resultat_obtenu = models.CharField(max_length=300, null=True, blank=True)
    activite_et_associations = models.TextField(null=True, blank=True)
    annee_debut = models.DateField()
    annee_fin = models.DateField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)


class Organisme(models.Model):
    nom = models.CharField(max_length=300)
    logo = models.ImageField(upload_to="SocialMedia/Image/")


class ActionBenevole(models.Model):
    organisme = models.ForeignKey(Organisme, on_delete=models.CASCADE, null=True, blank=True)
    nom_organisme = models.CharField(max_length=300)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, null=True, blank=True)
    nom_poste = models.CharField(max_length=300)
    cause = models.TextField(null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)


class Langue(models.Model):
    NIVEAU_LANGUE = (('debutant', 'Débutant'), ('intermediaire', 'Intermédiaire'), ('expert', 'Expert'))
    nom = models.CharField(max_length=300)
    niveau = models.CharField(max_length=300, choices=NIVEAU_LANGUE)
    profils = models.ManyToManyField('main_app.Profil', related_name="profils")
