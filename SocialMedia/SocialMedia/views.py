from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from main_app.models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect, QueryDict, HttpResponseNotFound
from django.template.response import TemplateResponse
from .models import *
from .forms import *
from django.views.generic import ListView
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta
import warnings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout, login, authenticate
from django.core import serializers
from django.core.serializers import json
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.tokens import default_token_generator
from .models import *
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string


# Haytham

def home(request):
    return render(request, 'SocialMedia/acceuil.html')


def profil(request):
    context = dict()
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        context['is_first'] = p.is_first_socialmedia
        if context['is_first']:
            p.is_first = False
            p.save()
        context['userInterfaceForm'] = UserInterfaceInfos()
        context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values(
            'poste').values('nom_poste').last()
        context['profil_experience'] = Experience.objects.filter(profil=request.user.profil, actuel=True).last()
        context['ecole'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=False).values(
            'ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=True).values(
            'nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['photoform'] = PhotoForm()
        context['formations'] = Formation.objects.filter(profil=request.user.profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=request.user.profil)
        context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])
        context['FormAjouterLangue'] = FormAjouterLangue()
        context['langues'] = LangueProfil.objects.filter(profil=request.user.profil)
        context['FormExperience'] = FormExperience()
        context['experiences'] = Experience.get_user_experiences(request.user)
        context['FormFormation'] = FormFormation()
        context['nom_entreprises'] = Entreprise.noms_entreprises()
        context['nom_postes'] = Poste.noms_postes()
        context['nom_ecoles'] = Ecole.noms_ecoles()
        context['nom_organismes'] = Organisme.noms_organismes()
        context['FormBenevolat'] = FormBenevolat()
        context['benevolats'] = ActionBenevole.get_user_benevolats(request.user)
        context['FormInformations'] = FormInformations()
        context['FormInformationsUser'] = FormInformationsUser()
        context['FormInformationsProfil'] = FormInformationsProfil()

        return render(request, 'SocialMedia/myprofil/myprofil.html', context)
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('main_app:log_in')


def changephotoprofil(request):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                p = request.user.profil
                p.photo_profil = photo
                p.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


def changephotocouverture(request):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                p = request.user.profil
                p.photo_couverture = photo
                p.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


def ajaxUser(request):
    if request.user.is_authenticated:
        pid = request.GET.get('pid')
        p = Profil.objects.get(id=pid)
        if p.user.last_login is not None:
            last_login = p.user.last_login. strftime("%m %b %y %I:%M")
        else:
            last_login = "Non connecté"
        context = {'statut': True,
                   'username': p.user.username,
                   'last_login': last_login,
                   'photo_profil': p.photo_profil.image.url
                   }
        return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


def log_in(request):
    if request.user.is_authenticated:
        return redirect('SocialMedia:myprofil')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                p = Profil.objects.get(user=user)
                p.user.last_login = now()
                login(request, user)
                return redirect('SocialMedia:login')
            else:
                messages.warning(request,
                                 "Compte Non Activé, Veuiller L'activer par l'email envoyé vers votre adresse electronique")
                return redirect('main_app:login')
        else:
            messages.warning(request, "Username Ou Mot De Passe Incorrect")
            return redirect('main_app:login')
    else:
        return redirect('main_app:login')


def groupesProfil(request):
    if request.user.is_authenticated:
        context = dict()
        if request.method == "GET" and 'is_ajax_request' in request.GET:
            groupes = list()
            for groupe in Groupe.objects.all():
                print(groupe.admins.all())
                if request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all() or request.user.profil in  groupe.adherents.all():
                    g = dict()
                    g['id'] = groupe.id
                    g['photo_profil'] = groupe.photo_profil.image.url
                    g['photo_couverture'] = groupe.photo_couverture.image.url
                    g['statut'] = groupe.statut_groupe
                    g['nom'] = groupe.nom
                    g['description'] = groupe.description
                    g['nbMembres'] = groupe.admins.all().count()+groupe.moderators.all().count()+groupe.adherents.all().count()
                    groupes.append(list(g.values()))
            paginator = Paginator(groupes, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            profilGroupes = list(paginator.get_page(page))
            isNumPagesExcessed = False
            previous_page_number = 1
            next_page_number = 1
            if page is None:
                page = 1
                previous_page_number = 1
                next_page_number = 2
            else:
                if int(page) > paginator.num_pages:
                    isNumPagesExcessed = True
                    page = paginator.num_pages
                    previous_page_number = page - 1
                    next_page_number = page
                elif int(page) < 1:
                    page = 1
                    previous_page_number = 1
                    next_page_number = 2
                else:
                    previous_page_number = int(page) - 1
                    next_page_number = int(page) + 1
            context = {
                'statut': True,
                'has_previous': paginator.get_page(page).has_previous(),
                'has_next': paginator.get_page(page).has_next(),
                'previous_page_number': previous_page_number,
                'next_page_number': next_page_number,
                'num_pages': paginator.num_pages,
                'current_page': page,
                'groupes': list(profilGroupes),
                'NumPagesExcessed': isNumPagesExcessed,
                'nbGroupes': len(groupes),
            }
            if context['nbGroupes'] == 0:
                context['msg'] = "Vous n'êtes pas membre d'aucun groupe"
            return JsonResponse(context, safe=False)
        else:
            p = Profil.objects.get(user=request.user)
            context['is_first'] = p.is_first_socialmedia
            if context['is_first']:
                    p.is_first = False
                    p.save()
            context['userInterfaceForm'] = UserInterfaceInfos()
            context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('poste').values(
                'nom_poste').last()
            context['poste_actuel_renseigne'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values(
                'nom_poste').last()
            context['ecole'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=False).values(
                    'ecole__nom').last()
            context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=True).values(
                    'nom_ecole').last()
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['photoform'] = PhotoForm()
            context['experiences'] = Experience.objects.filter(profil=request.user.profil)
            context['formations'] = Formation.objects.filter(profil=request.user.profil)
            context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=request.user.profil)
            context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
            profilGroupes = [groupe for groupe in Groupe.objects.all() if request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()]
            context['nbGroupes'] = len(profilGroupes)
            page = request.GET.get('page')
            paginator = Paginator(profilGroupes, 12)
            context['profilGroupes'] = paginator.get_page(page)
            context['nbGroupes'] = len(profilGroupes)
            if len(profilGroupes) == 0:
                context['msg'] = "Vous n'êtes pas membre d'aucun groupe"
                return render(request, 'SocialMedia/myprofil/groupesMyProfil.html', context)
            return render(request, 'SocialMedia/myprofil/groupesMyProfil.html', context)
        p = Profil.objects.get(user=request.user)
        context['is_first'] = p.is_first_socialmedia
        if context['is_first']:
            p.is_first = False
            p.save()
        context['userInterfaceForm'] = UserInterfaceInfos()
        context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values(
            'poste').values(
            'nom_poste').last()
        context['poste_actuel_renseigne'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values(
            'nom_poste').last()
        context['ecole'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=False).values(
            'ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=True).values(
            'nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['photoform'] = PhotoForm()
        context['experiences'] = Experience.objects.filter(profil=request.user.profil)
        context['formations'] = Formation.objects.filter(profil=request.user.profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=request.user.profil)
        context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
        return render(request, 'SocialMedia/myprofil/groupesMyProfil.html', context)
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('SocialMedia:home')
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')


def demandesProfil(request):
    if request.user.is_authenticated:
        context = dict()
        formDemande = demandeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            demande = DemandeAmi.objects.get(id=formDemande.cleaned_data['demande'])
            demande.statut = formDemande.cleaned_data['statut']
            demande.save()
            demandesAmis = list(DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).values())
            context = {'statut': demande.statut,
                       'ami': demande.emetteur.user.username,
                       'demande': demande.id,
                       'nbdemandes': len(demandesAmis),
                       'demandesAmis': demandesAmis,
                       }
            return JsonResponse(context, safe=False)
        else:
            demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id')
            paginator = Paginator(demandesAmis, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            context['formDemande'] = formDemande
            context['nbdemandes'] = demandesAmis.count()
            context['demandesAmis'] = paginator.get_page(page)
            context['photoform'] = PhotoForm()
<<<<<<< HEAD
            context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('poste').values('nom_poste').last()
            context['poste_actuel_renseigne'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('nom_poste').last()
            context['ecole'] = Formation.objects.filter(profil=request.user.profil,ecole__isnull=False).values('ecole__nom').last()
            context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=True).values('nom_ecole').last()
            context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                        request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])
            context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values(
                'poste').values('nom_poste').last()
            context['poste_actuel_renseigne'] = Experience.objects.filter(profil=request.user.profil,
                                                                          actuel=True).values('nom_poste').last()
            context['ecole'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=False).values(
                'ecole__nom').last()
            context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil,
                                                                   ecole__isnull=True).values('nom_ecole').last()
=======
            context['experience_profil'] = Experience.objects.filter(profil=request.user.profil, actuel=True).first()
            context['formation_profil'] = Formation.get_last_formation(request.user)

            print(Formation.get_last_formation(request.user))

>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
            return render(request, 'SocialMedia/myprofil/demandesMyProfil.html', context)
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('main_app:log_in')


def demandeViaAjax(request):
    demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id').values()
    paginator = Paginator(demandesAmis, 12)  # Show 3 Profiles per page
    page = request.GET.get('page')
    demAmis = list(paginator.get_page(page))
    isNumPagesExcessed = False
    previous_page_number = 1
    next_page_number = 1
    if page is None:
        page = 1
        previous_page_number = 1
        next_page_number = 2
    else:
        if int(page) > paginator.num_pages:
            isNumPagesExcessed = True
            page = paginator.num_pages
            previous_page_number = page - 1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page) - 1
            next_page_number = int(page) + 1
    context = {
        'statut': True,
        'has_previous': paginator.get_page(page).has_previous(),
        'has_next': paginator.get_page(page).has_next(),
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'demandesAmis': demAmis,
        'nbdemandes': demandesAmis.count(),
        'NumPagesExcessed': isNumPagesExcessed,
    }
    return JsonResponse(context, safe=False)


def mediaProfil(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            return render(request, "SocialMedia/myprofil/mediaProfil.html", )
        else:
            profiles = Profil.objects.all().order_by('-id')[:20]
            photoform = PhotoForm()
            albums = Album.objects.filter(user=request.user)
            for album in albums:
                for file in album.reseausocialfile_set.all():
                    print(file.date_telechargement)
            return render(request, 'SocialMedia/myprofil/mediaProfil.html',
                          {'profiles': profiles, 'photoform': photoform,
                           'is_first': request.user.profil.is_first_socialmedia,
                           'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('main_app:log_in')

<<<<<<< HEAD
def editInterface(request):
    if request.user.is_authenticated:
        form = UserInterfaceInfos(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                return
        else:
            form.username = request.user.username
            form.poste_actuel = Experience.objects.filter(profil=request.user.profil).values('poste').values(
                'nom_poste').last()
            form.poste_actuel_renseigne = Experience.objects.filter(profil=request.user.profil).values(
                'nom_poste').last()
            form.ecole = Formation.objects.filter(profil=request.user.profil).values('ecole').last()
            form.ecole_renseigne = Formation.objects.filter(profil=request.user.profil).values('nom_ecole').last()
            entreprise_actuelle = request.user.profil.entreprise
            entreprise_actuelle_renseignee = request.user.profil.entreprise.nom
            entreprise_ville = request.user.profil.entreprise.ville
            entreprise_pays = request.user.profil.entreprise.ville
            profil_ville = request.user.profil.ville
            profil_pays = request.user.profil.pays
            return render(request, 'SocialMedia/myprofil/forms/base_forms.html', {'formUserInterface': form})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

def editAbout(request):
    if request.user.is_authenticated:
        form = UserAboutEdit(request.POST or None)
        if request.method == "POST":
            user = User.objects.get(pk=request.user.pk)
            p = Profil.objects.get(user=request.user)
            user.first_name = request.POST.get('firstName')
            user.last_name = request.POST.get('lastName')
            user.save()
            p.facebook = request.POST.get('facebook')
            p.youtube = request.POST.get('youtube')
            p.instagram = request.POST.get('instagram')
            p.linkedin = request.POST.get('linkedin')
            p.date_naissance = request.POST.get('dateNaissance')
            p.entreprise = get_object_or_404(Entreprise, pk=request.POST.get('entreprise'))
            p.save()
            return HttpResponse("Edited")
        else:
            entreprises = Entreprise.objects.all()
            form = UserAboutEdit(initial={'entreprise': request.user.profil.entreprise})
            return render(request, 'SocialMedia/myprofil/forms/editAboutForm.html',
                          {'editForm': form, 'nom': 'A Propos de', 'entreprises': entreprises})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

def editExperience(request, pk):
    if request.user.is_authenticated:
        form = UserExperienceEdit(request.POST or None)
        if request.method == "POST":
            ps = Poste.objects.get(id=request.POST.get('poste'))
            ent = Entreprise.objects.get(id=request.POST.get('entreprise'))
            Ex = Experience.objects.get(id=pk)
            Ex.poste = ps
            Ex.entreprise = ent
            Ex.date_debut = request.POST.get('dateDebut')
            Ex.date_fin = request.POST.get('dateFin')
            Ex.description = request.POST.get('description')
            Ex.save()
            return redirect('SocialMedia:myprofil')
        else:
            exp = get_object_or_404(Experience, id=pk)
            poste = Experience.objects.get(id=pk).poste
            entreprise = Experience.objects.get(id=pk).entreprise
            postes = Poste.objects.all()
            entreprises = Entreprise.objects.all()
            form = UserExperienceEdit(initial={'poste': poste,
                                               'entreprise': entreprise,
                                               'dateDebut': exp.date_debut,
                                               'dateFin': exp.date_fin,
                                               'description': exp.description})
            return render(request, 'SocialMedia/myprofil/forms/editExperience.html',
                          {'editForm': form, 'exp': exp.id, 'nom': 'Experience De '})
=======

def suprimerAmi(request):
    pass


def findfriends(request):
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        friends_and_requests = DemandeAmi.objects.exclude(emetteur=request.user, )
        profiles = Profil.objects.all()
        return render(request, 'SocialMedia/myprofil/demandesMyProfil.html', {'profiles': profiles})
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

<<<<<<< HEAD
def editFormation(request, pk):
    if request.user.is_authenticated:
        form = UserFormationEdit(request.POST or None)
        if request.method == "POST":
            ecole = Ecole.objects.get(id=request.POST.get('ecole'))
            formation = Formation.objects.get(id=pk)
            formation.ecole = ecole
            formation.titre_formation = request.POST.get('titre_formation')
            formation.nom_formation = request.POST.get('nom_formation')
            formation.domaine = request.POST.get('domaine')
            formation.resultat_obtenu = request.POST.get('resultat_obtenu')
            formation.activite_et_associations = request.POST.get('activite_et_associations')
            formation.anneeDebut = request.POST.get('anneeDebut')
            formation.anneeFin = request.POST.get('anneeFin')
            formation.description = request.POST.get('description')
            formation.save()
            return redirect('SocialMedia:myprofil')
        else:
            formation = get_object_or_404(Formation, id=pk)
            ecole = Formation.objects.get(id=pk).ecole
            entreprise = Experience.objects.get(id=pk).entreprise
            ecoles = Ecole.objects.all()
            form = UserFormationEdit(initial={'titre_formation': formation.titre_formation,
                                              'ecole': ecole,
                                              'nom_formation': formation.nom_formation,
                                              'domaine': formation.domaine,
                                              'resultat_obtenu': formation.resultat_obtenu,
                                              'activite_et_associations': formation.activite_et_associations,
                                              'anneeDebut': formation.annee_debut,
                                              'anneeFin': formation.annee_fin,
                                              'description': formation.description, })
            return render(request, 'SocialMedia/myprofil/forms/editFormation.html',
                          {'editForm': form, 'nom': 'A Propos de', 'formation': formation.id, 'postes': ecoles})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')
=======

def chat(request):
    pass


def rechercherAmis(request):
    pass


class uploads(View):
    def get(self, request):
        photos_list = Image.objects.all()
        return render(self.request, 'SocialMedia/FileUploadTest.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.image.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)

>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21

# EndHaytham

# Chipop

@login_required
def search(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404

    # Contacts Search
    profils = Profil.objects.filter(Q(user__last_name__contains=keywords) | Q(user__first_name__contains=keywords),
                                    user__is_active=True).exclude(id=request.user.profil.id)

    # Groupes Search
    groupes = Groupe.objects.filter(nom__contains=keywords)

    # Offres d'emploi Search
    offres = OffreEmploi.objects.filter(Q(type_contrat__contains=keywords) | Q(diplome_requis__contains=keywords) | Q(
        description_poste__contains=keywords) | Q(profil_recherche__contains=keywords) | Q(
        presentation_entreprise__contains=keywords) | Q(type_emploi__contains=keywords) | Q(
        nom_poste__contains=keywords), en_cours=True)

    return render(request, 'SocialMedia/search/search_all.html',
                  {'keywords': keywords, 'profils': profils, 'groupes': groupes, 'offres': offres})

<<<<<<< HEAD
=======

@login_required
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
def search_members(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404

    # Contacts Search
    profils_list = Profil.objects.filter(Q(user__last_name__contains=keywords) | Q(user__first_name__contains=keywords),
                                         user__is_active=True).exclude(id=request.user.profil.id)

    paginator = Paginator(profils_list, 32)

    page = request.GET.get('page')
    profils = paginator.get_page(page)

    return render(request, 'SocialMedia/search/search_members.html', {'profils': profils, 'keywords': keywords})

<<<<<<< HEAD
=======

@login_required
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
def search_groupes(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404

    # Groupes Search
    groupes_list = Groupe.objects.filter(nom__contains=keywords)

    paginator = Paginator(groupes_list, 32)

    page = request.GET.get('page')
    groupes = paginator.get_page(page)

    return render(request, 'SocialMedia/search/search_groupes.html', {'groupes': groupes, 'keywords': keywords})

<<<<<<< HEAD
=======

@login_required
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
def search_offres(request):
    keywords = request.GET.get('keywords')
    duree = request.GET.get('duree')
    if keywords is None or keywords is "":
        raise Http404

    # Offres d'emploi Search
    offres_list = OffreEmploi.objects.filter(
        Q(type_contrat__contains=keywords) | Q(diplome_requis__contains=keywords) | Q(
            description_poste__contains=keywords) | Q(profil_recherche__contains=keywords) | Q(
            presentation_entreprise__contains=keywords) | Q(type_emploi__contains=keywords) | Q(
            nom_poste__contains=keywords), en_cours=True)

    if duree is not None and duree is not "":
        if duree is "semaine":
            one_week_ago = datetime.today() - timedelta(days=7)
            offres_list.filter(date_publication__gte=one_week_ago)
        elif duree is "mois":
            one_month_ago = datetime.today() - timedelta(days=31)
            offres_list.filter(date_publication__gte=one_month_ago)

    paginator = Paginator(offres_list, 32)

    page = request.GET.get('page')
    offres = paginator.get_page(page)

    return render(request, 'SocialMedia/search/search_offres.html', {'offres': offres, 'keywords': keywords})

<<<<<<< HEAD
=======

def test(request):
    return render(request, 'SocialMedia/test.html')


def ajouterLangue(request):
    formAjouterLangue = FormAjouterLangue(request.POST)

    if formAjouterLangue.is_valid():
        langue_profil = formAjouterLangue.save(commit=False)
        langue_profil.profil = request.user.profil
        langue_profil.save()

        langues = LangueProfil.objects.filter(profil=request.user.profil)
        liste_langues = render_to_string('SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues},
                                         request=request)
        return JsonResponse({'liste_langues': liste_langues})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_langue.html',
            {'FormAjouterLangue': formAjouterLangue},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def getModifierLangue(request):
    id_langue = request.GET.get('id_langue', None)

    if id_langue is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    langue_profil = LangueProfil.objects.get(id=id_langue)
    formModifierLangue = FormAjouterLangue(instance=langue_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_langue.html',
                  {'formModifierLangue': formModifierLangue, 'id_langue': id_langue})


def modifierLangue(request):
    id_langue = id = request.POST.get("id_langue")

    langue__profil = LangueProfil.objects.get(id=request.POST.get("id_langue"))

    formAjouterLangue = FormAjouterLangue(request.POST, instance=langue__profil)
    print(formAjouterLangue)

    if formAjouterLangue.is_valid():
        langue_profil = formAjouterLangue.save(commit=False)
        langue_profil.profil = request.user.profil
        langue_profil.save()

        langues = LangueProfil.objects.filter(profil=request.user.profil)

        liste_langues_profil = render_to_string('SocialMedia/myprofil/informations/liste_langues.html',
                                                {'langues': langues},request=request)
        return JsonResponse({'liste_langues_profil': liste_langues_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_langue.html',
            {'formModifierLangue': formAjouterLangue, 'id_langue': id_langue},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerLangue(request):
    id_langue = request.GET.get('id_langue', None)
    if id_langue is None:
        return Http404()

    LangueProfil.objects.get(id=id_langue).delete()

    langues = LangueProfil.objects.filter(profil=request.user.profil)
    # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
    return render(request, 'SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues})


def ajouterExperience(request):
    formExperience = FormExperience(request.POST)

    if formExperience.is_valid():
        experience_profil = formExperience.save(commit=False)
        experience_profil.profil = request.user.profil

        experience_profil.regler_date()

        if experience_profil.actuel:
            experience_profil.date_fin = None

        entreprise = get_object_or_none(Entreprise, nom=experience_profil.nom_entreprise)
        poste = get_object_or_none(Poste, nom_poste=experience_profil.nom_poste)

        if entreprise:
            experience_profil.entreprise = entreprise
        if poste:
            experience_profil.poste = poste

        experience_profil.save()

        experiences = Experience.get_user_experiences(request.user)

        liste_experiences = render_to_string('SocialMedia/myprofil/informations/liste_experiences.html',
                                            {'experiences': experiences},
                                            request=request)
        return JsonResponse({'liste_experiences': liste_experiences})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_experience.html',
            {'FormExperience': formExperience},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerExperience(request):
    id_experience = request.GET.get('id_experience', None)
    if id_experience is None:
        return Http404()

    Experience.objects.get(id=id_experience).delete()

    experiences = Experience.get_user_experiences(request.user)
    # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
    return render(request, 'SocialMedia/myprofil/informations/liste_experiences.html', {'experiences': experiences})


def getModifierExperience(request):
    id_experience = request.GET.get('id_experience', None)

    if id_experience is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    experience_profil = Experience.objects.get(id=id_experience)
    FormModifierExperience = FormExperience(instance=experience_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_experience.html',
                  {'FormModifierExperience': FormModifierExperience, 'id_experience': id_experience})


def modifierExperience(request):
    id_experience = request.POST.get("id_experience")
    experience__profil = Experience.objects.get(id=id_experience)

    formModifierExperience = FormExperience(request.POST, instance=experience__profil)

    if formModifierExperience.is_valid():
        experience = formModifierExperience.save(commit=False)
        experience.profil = request.user.profil

        experience.date_debut = experience.date_debut.replace(day=1)
        experience.date_fin = experience.date_fin.replace(day=1)

        if experience.actuel:
            experience.date_fin = None

        entreprise = get_object_or_none(Entreprise, nom=experience.nom_entreprise)
        poste = get_object_or_none(Poste, nom_poste=experience.nom_poste)

        if entreprise:
            experience.entreprise = entreprise
        else:
            experience.entreprise = None

        if poste:
            experience.poste = poste
        else:
            experience.poste = None

        experience.save()

        experiences = Experience.get_user_experiences(request.user)
        liste_benevolats_profil = render_to_string('SocialMedia/myprofil/informations/liste_experiences.html',
                                                   {'experiences': experiences},request=request)
        return JsonResponse({'liste_experiences': liste_benevolats_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_experience.html',
            {'FormModifierExperience': formModifierExperience, 'id_experience': id_experience},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def ajouterFormation(request):
    formFormation = FormFormation(request.POST)

    if formFormation.is_valid():
        formation_profil = formFormation.save(commit=False)
        formation_profil.profil = request.user.profil

        formation_profil.regler_date()

        ecole = get_object_or_none(Ecole, nom=formation_profil.nom_ecole)

        if ecole:
            formation_profil.nom_ecole = ecole.nom

        formation_profil.save()

        formations = Formation.get_user_formations(request.user)

        liste_formations = render_to_string('SocialMedia/myprofil/informations/liste_formations.html',
                                            {'formations': formations},
                                            request=request)
        return JsonResponse({'liste_formations': liste_formations})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_formation.html',
            {'FormFormation': formFormation},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerFormation(request):
    id_formation = request.GET.get('id_formation', None)
    if id_formation is None:
        return Http404()

    Formation.objects.get(id=id_formation).delete()

    formations = Formation.get_user_formations(request.user)
    return render(request, 'SocialMedia/myprofil/informations/liste_formations.html', {'formations': formations})


def getModifierFormation(request):
    id_formation = request.GET.get('id_formation', None)

    if id_formation is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    formation_profil = Formation.objects.get(id=id_formation)
    formFormation = FormFormation(instance=formation_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_formation.html',
                  {'FormFormation': formFormation, 'id_formation': id_formation})


def modifierFormation(request):
    id_formation = request.POST.get("id_formation")
    formation__profil = Formation.objects.get(id=id_formation)

    formModifierFormation = FormFormation(request.POST, instance=formation__profil)

    if formModifierFormation.is_valid():
        formation = formModifierFormation.save(commit=False)
        formation.profil = request.user.profil

        formation.regler_date()

        ecole = get_object_or_none(Ecole, nom=formation.nom_ecole)

        if ecole:
            formation.ecole = ecole
        else:
            formation.ecole = None

        formation.save()

        formations = Formation.get_user_formations(request.user)
        liste_formations_profil = render_to_string('SocialMedia/myprofil/informations/liste_formations.html',
                                                   {'formations': formations},request=request)
        return JsonResponse({'liste_formations': liste_formations_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_formation.html',
            {'FormFormation': formModifierFormation, 'id_formation': id_formation},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def ajouterBenevolat(request):
    formBenevolat = FormBenevolat(request.POST)

    if formBenevolat.is_valid():
        benevolat_profil = formBenevolat.save(commit=False)
        benevolat_profil.profil = request.user.profil

        benevolat_profil.regler_date()

        organisme = get_object_or_none(Organisme, nom=benevolat_profil.nom_organisme)
        poste = get_object_or_none(Poste, nom_poste=benevolat_profil.nom_poste)

        if organisme:
            benevolat_profil.organisme = organisme
        if poste:
            benevolat_profil.poste = poste

        benevolat_profil.save()

        benevolats = ActionBenevole.get_user_benevolats(request.user)
        liste_benevolats = render_to_string('SocialMedia/myprofil/informations/liste_benevolat.html',
                                            {'benevolats': benevolats},
                                            request=request)
        return JsonResponse({'liste_benevolats': liste_benevolats})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_benevolat.html',
            {'FormBenevolat': formBenevolat},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerBenevolat(request):
    id_benevolat = request.GET.get('id_benevolat', None)
    if id_benevolat is None:
        return Http404()

    ActionBenevole.objects.get(id=id_benevolat).delete()

    benevolats = ActionBenevole.get_user_benevolats(request.user)
    return render(request, 'SocialMedia/myprofil/informations/liste_benevolat.html', {'benevolats': benevolats})


def getModifierBenevolat(request):
    id_benevolat = request.GET.get('id_benevolat', None)

    if id_benevolat is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    benevolat_profil = ActionBenevole.objects.get(id=id_benevolat)

    formBenevolat = FormBenevolat(instance=benevolat_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_benevolat.html',
                  {'FormBenevolat': formBenevolat, 'id_benevolat': id_benevolat})


def modifierBenevolat(request):
    id_benevolat = request.POST.get("id_benevolat")

    benevolat__profil = ActionBenevole.objects.get(id=id_benevolat)

    formModifierBenevolat = FormBenevolat(request.POST, instance=benevolat__profil)

    if formModifierBenevolat.is_valid():
        benevolat = formModifierBenevolat.save(commit=False)
        benevolat.profil = request.user.profil

        benevolat.regler_date()

        poste = get_object_or_none(Poste, nom_poste=benevolat.nom_poste)
        organisme = get_object_or_none(Organisme, nom=benevolat.nom_organisme)

        if poste:
            benevolat.poste = poste
        else:
            benevolat.poste = None

        if organisme:
            benevolat.organisme = organisme
        else:
            benevolat.organisme = None

        benevolat.save()

        benevolats = ActionBenevole.get_user_benevolats(request.user)
        liste_benevolats_profil = render_to_string('SocialMedia/myprofil/informations/liste_benevolat.html',
                                                   {'benevolats': benevolats},request=request)
        return JsonResponse({'liste_benevolats': liste_benevolats_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_benevolat.html',
            {'FormBenevolat': formModifierBenevolat, 'id_benevolat': id_benevolat},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def getModifierInformations(request):
    formInformations = FormInformations(instance=request.user.profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_informations.html',
                  {'FormInformations': formInformations})


def modifierInformations(request):
    formInformations = FormInformations(request.POST, instance=request.user.profil)

    if formInformations.is_valid():
        formInformations.save()

        liste_informations = render_to_string('SocialMedia/myprofil/informations/liste_informations.html',
                                                   request=request)
        return JsonResponse({'liste_informations': liste_informations}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_informations.html',
            {'FormInformations': formInformations},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def getModifierInformationsProfil(request):
    formInformationsProfil = FormInformationsProfil(instance=request.user.profil)
    formInformationsUser = FormInformationsUser(instance=request.user)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_informations_profil.html',
                  {'FormInformationsProfil': formInformationsProfil, 'FormInformationsUser': formInformationsUser})


def modifierInformationsProfil(request):
    formInformationsProfil = FormInformationsProfil(request.POST, instance=request.user.profil)
    formInformationsUser = FormInformationsUser(request.POST, instance=request.user)

    if formInformationsProfil.is_valid() and formInformationsUser.is_valid():
        formInformationsProfil.save()
        formInformationsUser.save()
        liste_informations_profil = render_to_string('SocialMedia/myprofil/informations/liste_informations_profil.html',
                                                     {'user': request.user})
        return JsonResponse({'liste_informations_profil': liste_informations_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_informations_profil.html',
            {'FormInformationsProfil': formInformationsProfil, 'FormInformationsUser': formInformationsUser},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)
    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)

# Offre d'emploi


def creer_offre(request):

    if request.method == "POST":
        formCreerEmploiEntreprise = FormCreerEmploiEntreprise(request.POST)
        if formCreerEmploiEntreprise.is_valid():
            entreprise_a_creer = formCreerEmploiEntreprise.save(commit=False)
            entreprise = get_object_or_none(Entreprise,nom__iexact=entreprise_a_creer.nom)
            if entreprise is None:
                request.session['nom_entreprise'] = entreprise_a_creer.nom
            else:
                request.session['nom_entreprise'] = entreprise.nom
            return redirect('SocialMedia:creer_entreprise')

        else:
            nom_entreprise = formCreerEmploiEntreprise.data.get('nom', None)
            if nom_entreprise is not None:
                request.session['nom_entreprise'] = nom_entreprise
            return redirect('SocialMedia:creer_entreprise')

    formCreerEmploiEntreprise = FormCreerEmploiEntreprise()
    noms_entreprises = Entreprise.noms_entreprises()
    return render(request, 'SocialMedia/offre_emploi//creer_offre.html',{'FormCreerEmploiEntreprise':formCreerEmploiEntreprise,'noms_entreprises':noms_entreprises})


def creer_entreprise(request):
    if request.method == "POST":
        formCreerEntreprise = FormCreerEntreprise(request.POST)
        if formCreerEntreprise.is_valid():
            formCreerEntreprise.save()
            return render(request,'SocialMedia/offre_emploi/creer_offre_emploi.html') # Ajout form Creer Offre

    formCreerEntreprise = FormCreerEntreprise()
    nom_entreprise = request.session.get('nom_entreprise','')
    request.session.pop("nom_entreprise", None)
    return render(request, 'SocialMedia/offre_emploi/creer_entreprise.html',
                  {'formCreerEntreprise': formCreerEntreprise,'nom_entreprise':nom_entreprise})

>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
# EndChipop

# Haytham
def getProfil(request, pk):
    context = dict()
    try:
        if request.user.profil == Profil.objects.get(id=pk):
            return redirect('SocialMedia:myprofil')
        profil = Profil.objects.get(id=pk)
        if DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                     Q(recepteur=profil) | Q(recepteur=request.user.profil), statut=3).exists():
            messages.warning(request, "Le profil recherché est bloqué!")
            return redirect('SocialMedia:myprofil')
        context['profil'] = profil
        context['poste_actuel'] = Experience.objects.filter(profil=profil, actuel=True).values('poste').values(
            'nom_poste').last()
        context['poste_actuel_renseigne'] = Experience.objects.filter(profil=profil, actuel=True).values(
            'nom_poste').last()
        context['ecole'] = Formation.objects.filter(profil=profil, ecole__isnull=False).values('ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=profil, ecole__isnull=True).values(
            'nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['experiences'] = Experience.objects.filter(profil=profil)
        context['formations'] = Formation.objects.filter(profil=profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=profil)
        context['is_followed'] = Suivie.objects.filter(followed_profil=profil, follower=request.user.profil).exists()
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil), Q(recepteur=request.user.profil) | Q(recepteur=profil), statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil, statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil, statut=0).exists()
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()])
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        return render(request, 'SocialMedia/profil/profil.html', context)
    except Profil.DoesNotExist:
        raise Http404

def followProfil(request, pk):
    if request.user.is_authenticated:
        context = dict()
        try:
            s = Suivie.objects.get(followed_profil=Profil.objects.get(id=pk), follower=request.user.profil)
            s.delete()
            context['statut'] = True
            context['message'] = "Profile devient non suivi"
            context['follow'] = False
            return JsonResponse(context, safe=False)
        except Suivie.DoesNotExist:
            Suivie.objects.create(followed_profil=get_object_or_404(Profil, id=pk), follower=request.user.profil)
            context['statut'] = True
            context['message'] = "Profile est suivi"
            context['follow'] = True
            return JsonResponse(context, safe=False)
        except Profil.DoesNotExist:
            context['statut'] = False
            context['message'] = "Profil a ete supprimé, veuiller actualiser!"
            context['follow'] = False
            return JsonResponse(context, safe=False)

    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

def FriendsRequests(request, pk):
    if request.user.is_authenticated:
        context = dict()
        rep = int(request.POST.get('rep'))
        try:
            profil = Profil.objects.get(id=pk)
            demande = DemandeAmi.objects.get(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                             Q(recepteur=request.user.profil) | Q(recepteur=profil))
            context['statut'] = True
            if rep == -1:
                context['message'] = "La demande de {} à été annulée".format(profil.user.username)
                context['friend'] = False
                demande.delete()
            elif rep == -2:
                context['message'] = "{} à été supprimé de la liste des amis".format(profil.user.username)
                context['friend'] = False
                demande.delete()
            elif rep == 0:
                demande.statut = rep
                demande.emetteur = request.user.profil
                demande.recepteur = profil
                context['message'] = "Demande à été envoyée à {}".format(profil.user.username)
                context['friend'] = False
                demande.save()
            elif rep == 1:
                demande.statut = rep
                context['message'] = "Vous etes Ami Avec {}".format(profil.user.username)
                context['friend'] = True
                demande.save()
            elif rep == 2:
                demande.statut = rep
                context['message'] = "Vous avez refuser la demande de {}".format(profil.user.username)
                context['friend'] = False
                demande.save()
            elif rep == 3:
                demande.statut = rep
                context['message'] = "{} à été bloqué.".format(profil.user.username)
                context['friend'] = False
                demande.save()
            return JsonResponse(context, safe=False)
        except DemandeAmi.DoesNotExist:
            try:
                profil = Profil.objects.get(id=pk)
                if rep == 0:
                    DemandeAmi.objects.create(recepteur=profil, emetteur=request.user.profil, statut=rep)
                    context['statut'] = True
                    context['message'] = "Demande à été envoyée à {}".format(profil.user.username)
                    context['friend'] = False
                elif rep == 3:
                    DemandeAmi.objects.create(emetteur=request.user.profil, recepteur=profil, statut=rep)
                    context['message'] = "{} à été bloqué.".format(profil.user.username)
                    context['friend'] = False
                return JsonResponse(context, safe=False)
            except Profil.DoesNotExist:
                context['statut'] = False
                context['message'] = "Profil a ete supprimé, veuiller actualiser!"
                context['friend'] = False
                return JsonResponse(context, safe=False)
        except Profil.DoesNotExist:
            context['statut'] = False
            context['message'] = "Profil a ete supprimé, veuiller actualiser!"
            context['friend'] = False
            return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

def getRequestsUpdates(request, pk):
    if request.user.is_authenticated:
        context = dict()
        profil = Profil.objects.get(id=pk)
        context['statut'] = True
        context['is_blocked'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                          Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                          statut=3).exists()
        context['is_followed'] = Suivie.objects.filter(followed_profil=profil, follower=request.user.profil).exists()
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        return JsonResponse(context, safe=False)

def getProfilGroupes(request, pk):
    context = dict()
    try:
        profil = Profil.objects.get(id=pk)
        if request.method == "GET" and 'is_ajax_request' in request.GET:
            groupes = list()
            for groupe in Groupe.objects.all():
                print(groupe.admins.all())
                if profil in groupe.admins.all() or profil in groupe.moderators.all() or profil in  groupe.adherents.all():
                    g = dict()
                    g['id'] = groupe.id
                    g['photo_profil'] = groupe.photo_profil.image.url
                    g['photo_couverture'] = groupe.photo_couverture.image.url
                    g['statut'] = groupe.statut_groupe
                    g['nom'] = groupe.nom
                    g['description'] = groupe.description
                    g['nbMembres'] = groupe.admins.all().count()+groupe.moderators.all().count()+groupe.adherents.all().count()
                    groupes.append(list(g.values()))
            paginator = Paginator(groupes, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            profilGroupes = list(paginator.get_page(page))
            isNumPagesExcessed = False
            previous_page_number = 1
            next_page_number = 1
            if page is None:
                page = 1
                previous_page_number = 1
                next_page_number = 2
            else:
                if int(page) > paginator.num_pages:
                    isNumPagesExcessed = True
                    page = paginator.num_pages
                    previous_page_number = page - 1
                    next_page_number = page
                elif int(page) < 1:
                    page = 1
                    previous_page_number = 1
                    next_page_number = 2
                else:
                    previous_page_number = int(page) - 1
                    next_page_number = int(page) + 1
            context = {
                'statut': True,
                'has_previous': paginator.get_page(page).has_previous(),
                'has_next': paginator.get_page(page).has_next(),
                'previous_page_number': previous_page_number,
                'next_page_number': next_page_number,
                'num_pages': paginator.num_pages,
                'current_page': page,
                'groupes': list(profilGroupes),
                'NumPagesExcessed': isNumPagesExcessed,
                'nbGroupes': len(groupes),
            }
            if context['nbGroupes'] == 0:
                context['msg'] = profil.user.username+" n'est pas un membre d'aucun groupe"
            return JsonResponse(context, safe=False)
        else:
            profilGroupes = [groupe for groupe in Groupe.objects.all() if profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()]
            if request.user.profil == Profil.objects.get(id=pk):
                messages.info(request, "C'est votre profil")
                return redirect('SocialMedia:groupes')
            if DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil, statut=3).exists():
                messages.warning(request, "Les groupes concernent un profil bloqué!")
                return redirect('SocialMedia:myprofil')
            if DemandeAmi.objects.filter(recepteur=request.user.profil, emetteur=profil, statut=3).exists():
                messages.warning(request, "Les groupes du profil recherché vous a bloqué!")
                return redirect('SocialMedia:myprofil')
            context['profil'] = profil
            context['poste_actuel'] = Experience.objects.filter(profil=profil, actuel=True).values('poste').values(
                'nom_poste').last()
            context['poste_actuel_renseigne'] = Experience.objects.filter(profil=profil, actuel=True).values(
                'nom_poste').last()
            context['ecole'] = Formation.objects.filter(profil=profil, ecole__isnull=False).values('ecole__nom').last()
            context['ecole_renseignee'] = Formation.objects.filter(profil=profil, ecole__isnull=True).values(
                'nom_ecole').last()
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['experiences'] = Experience.objects.filter(profil=profil)
            context['formations'] = Formation.objects.filter(profil=profil)
            context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=profil)
            context['is_followed'] = Suivie.objects.filter(followed_profil=profil, follower=request.user.profil).exists()
            context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                             Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                             statut=1).exists()
            context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                       statut=0).exists()
            context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                                   statut=0).exists()
<<<<<<< HEAD
            page = request.GET.get('page')
            paginator = Paginator(profilGroupes, 12)
            context['profilGroupes'] = paginator.get_page(page)
            context['nbGroupes'] = len(profilGroupes)
            if len(profilGroupes) == 0:
                context['msg'] = profil.user.username+" n'est pas un membre d'aucun groupe"
                return render(request, 'SocialMedia/profil/groupesProfil.html', context)
            return render(request, 'SocialMedia/profil/groupesProfil.html', context)
    except Profil.DoesNotExist:
        messages.error(request, "Le Profil Que Vous cherchez n'existe pas!")
        return redirect('SocialMedia:myprofil')
=======
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        context['groupes'] = Groupe.objects.filter(
            id__in=DemandeGroupe.objects.filter(emetteur=profil, reponse=True).values('groupe_recepteur'))
        context['profilGroupes'] = [groupe for groupe in Groupe.objects.all() if
                                    profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()]
        if len(context['profilGroupes']) == 0:
            context['msg'] = profil.user.username + " n'est pas un membre d'aucun groupe"
            return render(request, 'SocialMedia/profil/groupesProfil.html', context)
        return render(request, 'SocialMedia/profil/groupesProfil.html', context)
    except Profil.DoesNotExist:
        messages.error(request, "Le Profil Que Vous cherchez n'existe pas!")
        return redirect('SocialMedia:myprofil')
    except DemandeGroupe.DoesNotExist:
        context['msg'] = "Le profil ne s'appartient à aucun groupe"
        return render(request, 'SocialMedia/profil/groupesProfil.html', context)

>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21

def groupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        try:
            groupe = Groupe.objects.get(id=pk)
            page = request.GET.get('page', 1)
            statuts = Statut.objects.filter(mur_groupe=groupe, is_group_statut=True)
            paginator = Paginator(statuts, 2)
            context['statuts'] = paginator.get_page(page)
            context['now'] = now()
            context['groupe'] = groupe
            context['statutForm'] = StatutsForm()
            context['photoform'] = PhotoForm()
            context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
            context['is_request_sent'] = groupe.demandegroupe_set.filter(emetteur=request.user.profil, groupe_recepteur=groupe, reponse=False).exists()
            context['nbMembers'] = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user).count()
            return render(request, 'SocialMedia/groupe/groupe1.html', context)
        except Groupe.DoesNotExist or Profil.DoesNotExist:
            raise Http404
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')


def demandesGroupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        groupe = Groupe.objects.get(id=pk)
<<<<<<< HEAD
        if request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all():
            formDemande = demandeGroupeForm(request.POST or None)
            if request.method == "POST" and formDemande.is_valid():
                demande = DemandeGroupe.objects.get(id=formDemande.cleaned_data['demande'])
                context['demande'] = demande.id
                if formDemande.cleaned_data['reponse'] == 1:
                    demande.reponse = formDemande.cleaned_data['reponse']
                    demande.save()
                    groupe.adherents.add(demande.emetteur)
                    groupe.save()
                    context['reponse'] = demande.reponse
                    context['message'] = 'demande de {} à été approuvée'.format(demande.emetteur.user.username)
                elif formDemande.cleaned_data['reponse'] == 0:
                    context['message'] = 'demande de {} à été refusée'.format(demande.emetteur.user.username)
                    context['reponse'] = 0
                    demande.delete()
                context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
                context['statut'] = True,
                return JsonResponse(context,safe=False)
            elif request.method == "GET":
                demandesGroupe = groupe.demandegroupe_set.filter(reponse=False).order_by('id')
                paginator = Paginator(demandesGroupe, 12)  # Show 12 Profiles per page
                page = request.GET.get('page')
                context['formDemande'] = formDemande
                context['nbdemandes'] = demandesGroupe.count()
                context['demandesGroupe'] = paginator.get_page(page)
                context['photoform'] = PhotoForm()
                context['groupe'] = groupe
                context['nbMembers'] = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user).count()
                context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
                context['is_request_sent'] = groupe.demandegroupe_set.filter(emetteur=request.user.profil, groupe_recepteur=groupe, reponse=False).exists()
                return render(request, 'SocialMedia/groupe/demandes_groupe.html', context)
        else:
            messages.error(request, "Vous n'avez pas le droit de valider cette action, s'il s'agit d'une erreur veuiller nous contacter.")
            return redirect(groupe.get_absolute_url())
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')

def demandesGroupeViaAjax(request, pk):
    groupe = Groupe.objects.get(id=pk)
    demandesGroupe = DemandeGroupe.objects.filter(groupe_recepteur=groupe, reponse=False).order_by('id').values()
    paginator = Paginator(demandesGroupe, 12)  # Show 12 Profiles per page
    page = request.GET.get('page')
    demGroupe = list(paginator.get_page(page))
    isNumPagesExcessed = False
    previous_page_number = 1
    next_page_number = 1
    if page is None:
        page = 1
        previous_page_number = 1
        next_page_number = 2
    else:
        if int(page) > paginator.num_pages:
            isNumPagesExcessed = True
            page = paginator.num_pages
            previous_page_number = page - 1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page) - 1
            next_page_number = int(page) + 1
    context = {
        'statut': True,
        'has_previous': paginator.get_page(page).has_previous(),
        'has_next': paginator.get_page(page).has_next(),
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'demandesGroupe': demGroupe,
        'nbdemandes': demandesGroupe.count(),
        'NumPagesExcessed': isNumPagesExcessed,
        'nbMembres': (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().count()
    }
    return JsonResponse(context, safe=False)

def membresGroupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        groupe = Groupe.objects.get(id=pk)
        formDemande = membresAdminForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            profil = get_object_or_404(Profil, id=formDemande.cleaned_data['profil'])
            if formDemande.cleaned_data['action'] == 3:
                groupe.admins.add(profil)
                groupe.moderators.remove(profil)
                groupe.adherents.remove(profil)
                groupe.save()
                context['message'] = '{} devient Administrateur.'.format(profil.user.username)
            elif formDemande.cleaned_data['action'] == 2:
                groupe.moderators.add(profil)
                groupe.admins.remove(profil)
                groupe.adherents.remove(profil)
                groupe.save()
                context['message'] = '{} devient Moderateur.'.format(profil.user.username)
            elif formDemande.cleaned_data['action'] == 1:
                groupe.admins.remove(profil)
                groupe.moderators.remove(profil)
                groupe.adherents.add(profil)
                groupe.save()
                context['message'] = '{} devenu Adherent.'.format(profil.user.username)
            elif formDemande.cleaned_data['action'] == 0:
                groupe.admins.remove(profil)
                groupe.moderators.remove(profil)
                groupe.adherents.remove(profil)
=======
        formDemande = demandeGroupeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid() and request.user.profil in (
                groupe.admins.all() or groupe.moderators.all()):
            demande = DemandeGroupe.objects.get(id=formDemande.cleaned_data['demande'])
            if formDemande.cleaned_data['reponse'] == 1:
                demande.reponse = formDemande.cleaned_data['reponse']
                demande.save()
                groupe.adherents.add(demande.emetteur)
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
                groupe.save()
                context['message'] = '{} à été Banné.'.format(profil.user.username)
            else:
<<<<<<< HEAD
                context['statut'] = False
                return JsonResponse(context,safe=False)
            groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user)
            context['statut'] = True
            context['nbMembers'] = groupeMembers.count()
            context['profil'] = profil.id
            return JsonResponse(context,safe=False)
=======
                context['message'] = 'demande de {} à été refusée'.format(demande.emetteur.user.username)
                context['reponse'] = 0
                demande.delete()
            context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
            demandesGroupe = list(DemandeGroupe.objects.filter(groupe_recepteur=groupe, reponse=False).values())
            context['statut'] = True,
            context['nbdemandes'] = len(demandesGroupe)
            context['demande'] = demande.id
            context['demandesGroupe'] = demandesGroupe
            return JsonResponse(context, safe=False)
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
        elif request.method == "GET":
            groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user)
            paginator = Paginator(groupeMembers, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            context['formDemande'] = formDemande
            context['nbMembers'] = groupeMembers.count()
            context['members'] = paginator.get_page(page)
            context['photoform'] = PhotoForm()
            context['groupe'] = groupe
            context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
<<<<<<< HEAD
            context['is_request_sent'] = groupe.demandegroupe_set.filter(emetteur=request.user.profil, groupe_recepteur=groupe, reponse=False).exists()
            return render(request, 'SocialMedia/groupe/membres_groupe.html', context)
=======
            return render(request, 'SocialMedia/groupe/demandes_groupe.html', context)
        else:
            messages.error(request,
                           "Vous n'avez pas le droit de valider cette action, s'il s'agit d'une erreur veuiller nous contacter.")
            return redirect('SocialMedia:myprofil')
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')

<<<<<<< HEAD
def membersGroupeViaAjax(request, pk):
=======

def demandesGroupeViaAjax(request, pk):
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
    groupe = Groupe.objects.get(id=pk)
    users_ID = list()
    groupeMembers = dict()
    if "admins" in request.GET:
        groupeMembers = groupe.admins.all().distinct().exclude(user=request.user).values()
    elif "moderators" in request.GET:
        groupeMembers = groupe.moderators.all().distinct().exclude(user=request.user).values()
    elif "adherents" in request.GET:
        groupeMembers = groupe.adherents.all().distinct().exclude(user=request.user).values()
    else:
        groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user).values()
    paginator = Paginator(groupeMembers, 12)  # Show 12 Profiles per page
    page = request.GET.get('page')
    memGroupe = paginator.get_page(page)
    isNumPagesExcessed = False
    previous_page_number = 1
    next_page_number = 1
    if page is None:
        page = 1
        previous_page_number = 1
        next_page_number = 2
    else:
        if int(page) > paginator.num_pages:
            isNumPagesExcessed = True
            page = paginator.num_pages
            previous_page_number = page - 1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page) - 1
            next_page_number = int(page) + 1
    context = {
        'statut': True,
        'has_previous': paginator.get_page(page).has_previous(),
        'has_next': paginator.get_page(page).has_next(),
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'membersGroupe': list(memGroupe),
        'nbMembers': groupeMembers.count(),
        'NumPagesExcessed': isNumPagesExcessed,
        'nbMembres': (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(id=request.user.profil.id).count(),
        'is_admin' : groupe.admins.filter(user=request.user).exists()
    }
    return JsonResponse(context, safe=False)

def joinGroupeViaAjax(request, pk):
    if request.user.is_authenticated:
        context = dict()
        if request.method == "POST":
            try:
                print(request.POST.get('userRequestGroupe'))
                if request.POST.get('userRequestGroupe') == "1":
                    print('send request')
                    if DemandeGroupe.objects.filter(emetteur=Profil.objects.get(user=request.user), groupe_recepteur=Groupe.objects.get(id=pk), reponse=False).exists():
                        DemandeGroupe.objects.filter(emetteur=Profil.objects.get(user=request.user),
                                                     groupe_recepteur=Groupe.objects.get(id=pk), reponse=False).delete()
                    DemandeGroupe.objects.create(emetteur=Profil.objects.get(user=request.user), groupe_recepteur=Groupe.objects.get(id=pk), reponse=False)
                    context['statut'] = True
                    context['msg'] = "Demande envoyée avec succé"
                    return JsonResponse(context, safe=False)
                elif request.POST.get('userRequestGroupe') == "0":
                    print('cancel membership request')
                    groupe = Groupe.objects.get(id=pk)
                    groupe.admins.remove(request.user.profil)
                    groupe.moderators.remove(request.user.profil)
                    groupe.adherents.remove(request.user.profil)
                    groupe.save()
                    DemandeGroupe.objects.filter(emetteur=request.user.profil, groupe_recepteur=groupe).delete()
                    context['statut'] = True
                    context['msg'] = "Vous n'êtes plus memebre de ce groupe"
                    return JsonResponse(context, safe=False)
                elif request.POST.get('userRequestGroupe') == "-1":
                    print('cancel request')
                    DemandeGroupe.objects.get(emetteur=request.user.profil, groupe_recepteur=Groupe.objects.get(id=pk)).delete()
                    context['statut'] = True
                    context['msg'] = "Demande annulée"
                    return JsonResponse(context, safe=False)
            except Exception as e:
                context['statut'] = False
                context['msg'] = str(e)
                return JsonResponse(context, safe=False)
        else:
            context['statut'] = False
            return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')

def getMoreComments(request, pk):
    context = dict()
    statutid = int(request.GET.get('statutid'))
    page = int(request.GET.get('page'))
    groupe = Groupe.objects.get(id=pk)
    statut = Statut.objects.get(mur_groupe=groupe,id=statutid)
    comments = statut.commentaire_set.all()
    paginator = Paginator(comments, 2)
    try:
        cmts = paginator.page(page)
    except PageNotAnInteger:
        cmts = paginator.page(1)
    except EmptyPage:
        cmts = paginator.page(paginator.num_pages)
    print(statut.id)
    return render(request, 'SocialMedia/groupe/comments/commentaires_groupe.html', {'comments':cmts, 'statutid':statutid, 'numPages':paginator.num_pages})

<<<<<<< HEAD

def changephotoprofilgroupe(request, pk):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                groupe = Groupe.objects.get(id=pk)
                groupe.photo_profil = photo
                groupe.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


def changephotocouverturegroupe(request, pk):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                groupe = Groupe.objects.get(id=pk)
                groupe.photo_couverture = photo
                groupe.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


# EndHaytham
#Chipop
def test(request):
    return render(request, 'SocialMedia/test.html')

def ajouterLangue(request):
    data = request.POST.get('data', None)

    formAjouterLangue = FormAjouterLangue(request.POST)

    if formAjouterLangue.is_valid():
        langue_profil = formAjouterLangue.save(commit=False)
        langue_profil.profil = request.user.profil
        langue_profil.save()

        langues = LangueProfil.objects.filter(profil=request.user.profil)
        # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
        return render(request, 'SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues})
    else:
        return JsonResponse({'messagee': 'Invalid'}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)

def getModifierLangue(request):
    id_langue = request.GET.get('id_langue', None)

    print(id_langue)

    if id_langue is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    langue_profil = LangueProfil.objects.get(id=id_langue)
    formModifierLangue = FormAjouterLangue(instance=langue_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_langue.html',
                  {'formModifierLangue': formModifierLangue,'id_langue':id_langue})

def modifierLangue(request):
    data = request.POST.get('data', None)
=======
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21

# chipop custom functions

<<<<<<< HEAD
    formAjouterLangue = FormAjouterLangue( request.POST,instance = langue__profil)
    print(formAjouterLangue)

    if formAjouterLangue.is_valid():
        langue_profil = formAjouterLangue.save(commit=False)
        langue_profil.profil = request.user.profil
        langue_profil.save()

        langues = LangueProfil.objects.filter(profil=request.user.profil)
        # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
        return render(request, 'SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues})
    else:
        return JsonResponse({'messagee': 'Invalid'}, safe=False)
    return JsonResponse({'messagee': 'HELLO'}, safe=False)

def supprimerLangue(request):
=======
def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21


<<<<<<< HEAD
    LangueProfil.objects.get(id=id_langue).delete()

    langues = LangueProfil.objects.filter(profil=request.user.profil)
    # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
    return render(request, 'SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues})

=======
def generer_form_errors(form):
    message_erreur = ""
    for key, value in form.errors.items():
        message_erreur += key + " " + value.as_text()
    return message_erreur
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21
