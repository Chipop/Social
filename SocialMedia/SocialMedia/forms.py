from django import forms
from .models import *
from main_app.models import *
from django.contrib.auth.models import User
from datetime import datetime



class PhotoForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Image
        fields = '__all__'


class demandeForm(forms.Form):
    demande = forms.IntegerField(widget=forms.HiddenInput)
    statut = forms.IntegerField(widget=forms.HiddenInput)


class demandeGroupeForm(forms.Form):
    demande = forms.IntegerField(widget=forms.HiddenInput)
    reponse = forms.IntegerField(widget=forms.HiddenInput)

class membresAdminForm(forms.Form):
    profil = forms.IntegerField(widget=forms.HiddenInput)
    action = forms.IntegerField(widget=forms.HiddenInput)


class UserInterfaceInfos(forms.Form):
    entreprises = formations = dict()
    postes = dict()
    for f in Formation.objects.all():
        formations[f.nom_ecole] = f

    for p in Poste.objects.all():
        postes[p.nom_poste] = p
    username = forms.CharField(max_length=255)
    poste_actuel = forms.ChoiceField(choices=postes)
    poste_actuel_renseigne = forms.CharField(max_length=255)
    ecole = forms.ChoiceField(choices=formations)
    ecole_renseigne = forms.CharField(max_length=255)
    entreprise_actuelle = forms.ChoiceField(choices=entreprises)
    entreprise_actuelle_renseignee = forms.CharField(max_length=255)
    entreprise_ville = forms.CharField(max_length=255)
    entreprise_pays = forms.CharField(max_length=255)
    profil_ville = forms.CharField(max_length=255)
    profil_pays = forms.CharField(max_length=255)


class UserAboutEdit(forms.Form):
    nom = forms.CharField(initial="A Propos De ")
    facebook = forms.URLField()
    youtube = forms.URLField()
    instagram = forms.URLField()
    linkedin = forms.URLField()
    firstName = forms.CharField(max_length=255, )
    lastName = forms.CharField(max_length=255)
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    dateNaissance = forms.DateField()


class UserExperienceEdit(forms.Form):
    poste = forms.ModelChoiceField(queryset=Poste.objects.all())
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    dateDebut = forms.DateField()
    dateFin = forms.DateField()
    description = forms.CharField(widget=forms.Textarea)


class UserFormationEdit(forms.Form):
    titre_formation = forms.CharField(max_length=255)
    ecole = forms.ModelChoiceField(queryset=Ecole.objects.all())
    nom_formation = forms.CharField(max_length=255)
    domaine = forms.CharField(max_length=255)
    resultat_obtenu = forms.DecimalField(max_digits=5)
    activite_et_associations = forms.CharField(widget=forms.Textarea)
    anneeDebut = forms.DateField()
    anneeFin = forms.DateField()
    description = forms.CharField(widget=forms.Textarea)


class FormAjouterLangue(forms.ModelForm):
    class Meta:
        model = LangueProfil
        fields = ['langue', 'niveau']


class FormExperience(forms.ModelForm):
    actuel = models.BooleanField("Ceci est mon poste actuel")
    date_debut = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))
    date_fin = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))

    class Meta:
        model = Experience
        fields = ['nom_entreprise', 'nom_poste', 'date_debut', 'date_fin', 'actuel', 'description', 'lieu']


class FormFormation(forms.ModelForm):
    annee_debut = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))
    annee_fin = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))

    class Meta:
        model = Formation
        fields = ['nom_ecole', 'titre_formation', 'domaine', 'annee_debut', 'annee_fin', 'activite_et_associations',
                  'description']


class FormBenevolat(forms.ModelForm):
    date_debut = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))
    date_fin = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))

    class Meta:
        model = ActionBenevole
        fields = ['nom_organisme', 'nom_poste', 'cause', 'date_debut', 'date_fin', 'description']


<<<<<<< HEAD
class StatutsForm(forms.Form):
    contenu_statut = forms.CharField(widget=forms.Textarea(attrs={'rows':'1'}))



=======
class FormInformations(forms.ModelForm):
    date_naissance = forms.DateField(required=True,
                                     widget=forms.SelectDateWidget(years=range(datetime.now().year, 1940, -1)))
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21

    class Meta:
        model = Profil
        fields = ['date_naissance', 'website', 'tel', 'facebook', 'youtube', 'instagram', 'linkedin', 'twitter']


class FormInformationsProfil(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['formation_profil', 'experience_profil', 'resume', 'ville', 'pays']


class FormInformationsUser(forms.ModelForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=100)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class FormCreerEmploiEntreprise(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom']


class FormCreerEntreprise(forms.ModelForm):
    a_propos = forms.Textarea()
    logo = forms.ImageField(required=True)
    class Meta:
        model = Entreprise
        fields = ['nom',"typeEntreprise",'logo','a_propos','siege_social','annee_creation','specialisation']
