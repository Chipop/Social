from django import forms
from .models import *
from main_app.models import *
from django.contrib.auth.models import User


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
