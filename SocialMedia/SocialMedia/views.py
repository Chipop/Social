from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from main_app.models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect, QueryDict, HttpResponseNotFound
from django.template.response import TemplateResponse
from .models import *
from .forms import *
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
        context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('poste').values('nom_poste').last()
        context['poste_actuel_renseigne'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('nom_poste').last()
        context['ecole'] = Formation.objects.filter(profil=request.user.profil,ecole__isnull=False).values('ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=True).values('nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['photoform'] = PhotoForm()
        context['experiences'] = Experience.objects.filter(profil=request.user.profil)
        context['formations'] = Formation.objects.filter(profil=request.user.profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=request.user.profil)
        context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])

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
                context={'status':'success', 'url':photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo':'Veuiller Salectionner Une Image'}
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
                context={'status':'success', 'url':photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo':'Veuiller Salectionner Une Image'}
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
        context={'statut':True,
                 'username':p.user.username,
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
                messages.warning(request, "Compte Non Activé, Veuiller L'activer par l'email envoyé vers votre adresse electronique")
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


def supprimerDemande(request):
    pass

def demandesProfil(request):
    if request.user.is_authenticated:
        context = dict()
        formDemande = demandeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            demande = DemandeAmi.objects.get(id=formDemande.cleaned_data['demande'])
            demande.statut = formDemande.cleaned_data['statut']
            demande.save()
            demandesAmis = list(DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).values())
            context={'statut': demande.statut,
                     'ami':demande.emetteur.user.username,
                     'demande':demande.id,
                     'nbdemandes':len(demandesAmis),
                     'demandesAmis': demandesAmis,
                     }
            return JsonResponse(context,safe=False)
        else:
            demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id')
            paginator = Paginator(demandesAmis, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            context['formDemande'] = formDemande
            context['nbdemandes'] = demandesAmis.count()
            context['demandesAmis'] = paginator.get_page(page)
            context['photoform'] = PhotoForm()
            context['poste_actuel'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('poste').values('nom_poste').last()
            context['poste_actuel_renseigne'] = Experience.objects.filter(profil=request.user.profil, actuel=True).values('nom_poste').last()
            context['ecole'] = Formation.objects.filter(profil=request.user.profil,ecole__isnull=False).values('ecole__nom').last()
            context['ecole_renseignee'] = Formation.objects.filter(profil=request.user.profil, ecole__isnull=True).values('nom_ecole').last()
            context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                        request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])
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
            previous_page_number = page-1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page)-1
            next_page_number = int(page)+1
    context={
             'statut':True,
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
    return JsonResponse(context,safe=False)

def mediaProfil(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            return render(request, "SocialMedia/myprofil/mediaProfil.html",)
        else:
            profiles = Profil.objects.all().order_by('-id')[:20]
            photoform = PhotoForm()
            albums = Album.objects.filter(user=request.user)
            for album in albums:
                for file in album.reseausocialfile_set.all():
                    print(file.date_telechargement)
            return render(request, 'SocialMedia/myprofil/mediaProfil.html',{'profiles': profiles, 'photoform': photoform, 'is_first': request.user.profil.is_first_socialmedia,'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('main_app:log_in')

def suprimerAmi(request):
    pass

def findfriends(request):
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        friends_and_requests = DemandeAmi.objects.exclude(emetteur=request.user, )
        profiles = Profil.objects.all()
        return render(request, 'SocialMedia/myprofil/demandesMyProfil.html', {'profiles':profiles})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

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

def editInterface(request):
    if request.user.is_authenticated:
        form = UserInterfaceInfos(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                return
        else:
            form.username = request.user.username
            form.poste_actuel = Experience.objects.filter(profil=request.user.profil).values('poste').values('nom_poste').last()
            form.poste_actuel_renseigne = Experience.objects.filter(profil=request.user.profil).values('nom_poste').last()
            form.ecole = Formation.objects.filter(profil=request.user.profil).values('ecole').last()
            form.ecole_renseigne = Formation.objects.filter(profil=request.user.profil).values('nom_ecole').last()
            entreprise_actuelle = request.user.profil.entreprise
            entreprise_actuelle_renseignee = request.user.profil.entreprise.nom
            entreprise_ville = request.user.profil.entreprise.ville
            entreprise_pays = request.user.profil.entreprise.ville
            profil_ville = request.user.profil.ville
            profil_pays = request.user.profil.pays
            return render(request, 'SocialMedia/myprofil/forms/base_forms.html', {'formUserInterface':form})
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
            form = UserAboutEdit(initial={'entreprise':request.user.profil.entreprise})
            return render(request, 'SocialMedia/myprofil/forms/editAboutForm.html', {'editForm':form, 'nom': 'A Propos de', 'entreprises':entreprises})
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
            form = UserExperienceEdit(initial={'poste':poste,
                                               'entreprise':entreprise,
                                               'dateDebut':exp.date_debut,
                                               'dateFin':exp.date_fin,
                                               'description':exp.description})
            return render(request, 'SocialMedia/myprofil/forms/editExperience.html', {'editForm':form, 'exp':exp.id, 'nom': 'Experience De '})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

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
            form = UserFormationEdit(initial={'titre_formation':formation.titre_formation,
                                              'ecole':ecole,
                                              'nom_formation':formation.nom_formation,
                                              'domaine':formation.domaine,
                                              'resultat_obtenu':formation.resultat_obtenu,
                                              'activite_et_associations':formation.activite_et_associations,
                                              'anneeDebut':formation.annee_debut,
                                              'anneeFin':formation.annee_fin,
                                              'description':formation.description,})
            return render(request, 'SocialMedia/myprofil/forms/editFormation.html', {'editForm':form, 'nom': 'A Propos de', 'formation':formation.id, 'postes':ecoles})
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')

#EndHaytham
#Chipop

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

#EndChipop

#Haytham
def getProfil(request, pk):
    context = dict()
    try:
        if request.user.profil == Profil.objects.get(id=pk):
            return redirect('SocialMedia:myprofil')
        profil = Profil.objects.get(id=pk)
        if DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil), Q(recepteur=profil) | Q(recepteur=request.user.profil), statut=3).exists():
            messages.warning(request, "Le profil recherché est bloqué!")
            return redirect('SocialMedia:myprofil')
        context['profil'] = profil
        context['poste_actuel'] = Experience.objects.filter(profil=profil, actuel=True).values('poste').values('nom_poste').last()
        context['poste_actuel_renseigne'] = Experience.objects.filter(profil=profil, actuel=True).values('nom_poste').last()
        context['ecole'] = Formation.objects.filter(profil=profil, ecole__isnull=False).values('ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=profil, ecole__isnull=True).values('nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['experiences'] = Experience.objects.filter(profil=profil)
        context['formations'] = Formation.objects.filter(profil=profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=profil)
        context['is_followed'] = Suivie.objects.filter(followed_profil=profil, follower=request.user.profil).exists()
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil), Q(recepteur=request.user.profil) | Q(recepteur=profil), statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil, statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil, statut=0).exists()
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()])
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
            context['message'] = "Profile devenu non suivi"
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
            demande = DemandeAmi.objects.get(Q(emetteur=request.user.profil) | Q(emetteur=profil), Q(recepteur=request.user.profil) | Q(recepteur=profil))
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
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,statut=0).exists()
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

def groupe(request, pk):
    context = dict()
    try:
        groupe = Groupe.objects.get(id=pk)
        context['groupe'] = groupe
        context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
        context['nbMembers'] = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user).count()
        return render(request, 'SocialMedia/groupe/groupe.html', context)
    except Groupe.DoesNotExist:
        raise Http404

def demandesGroupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        groupe = Groupe.objects.get(id=pk)
        if request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all():
            formDemande = demandeGroupeForm(request.POST or None)
            print(formDemande)
            if request.method == "POST" and formDemande.is_valid():
                demande = DemandeGroupe.objects.get(id=formDemande.cleaned_data['demande'])
                context['demande'] = demande.id
                if formDemande.cleaned_data['reponse'] == 1:
                    demande.reponse = formDemande.cleaned_data['reponse']
                    demande.save()
                    groupe.adherents.add(demande.emetteur)
                    groupe.save()
                    context['reponse'] = demande.reponse
                    context['message'] = 'demande de {} à été acceptée'.format(demande.emetteur.user.username)
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
        if request.user.profil in groupe.admins.all():
            formDemande = membresAdminForm(request.POST or None)
            if request.method == "POST" and formDemande.is_valid():
                profil = get_object_or_404(Profil, id=formDemande.cleaned_data['profil'])
                if formDemande.cleaned_data['action'] == 3:
                    groupe.admins.add(profil)
                    groupe.moderators.remove(profil)
                    groupe.moderators.remove(profil)
                    groupe.save()
                    context['message'] = '{} est devenu Administrateur.'.format(profil.user.username)
                elif formDemande.cleaned_data['action'] == 2:
                    groupe.moderators.add(profil)
                    groupe.admins.remove(profil)
                    groupe.adherents.remove(profil)
                    groupe.save()
                    context['message'] = '{} est devenu Moderateur.'.format(profil.user.username)
                elif formDemande.cleaned_data['action'] == 1:
                    groupe.admins.remove(profil)
                    groupe.moderators.remove(profil)
                    groupe.adherents.add(profil)
                    groupe.save()
                    context['message'] = '{} est devenu Adherent.'.format(profil.user.username)
                elif formDemande.cleaned_data['action'] == 0:
                    groupe.admins.remove(profil)
                    groupe.moderators.remove(profil)
                    groupe.adherents.remove(profil)
                    groupe.save()
                    context['message'] = '{} à été Banné.'.format(profil.user.username)
                else:
                    context['statut'] = False
                    return JsonResponse(context,safe=False)
                groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(user=request.user)
                context['statut'] = True
                context['nbMembers'] = groupeMembers.count()
                context['profil'] = profil.id
                return JsonResponse(context,safe=False)
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
                return render(request, 'SocialMedia/groupe/membres_groupe.html', context)
        else:
            messages.error(request, "Vous n'avez pas le droit d'acces")
            return redirect(groupe.get_absolute_url())
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')

def membersGroupeViaAjax(request, pk):
    groupe = Groupe.objects.get(id=pk)
    users_ID = list()
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
        'nbMembres': (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(id=request.user.profil.id).count()
    }
    return JsonResponse(context, safe=False)
"""
def joinGroupe(request, pk):
    if request.user.is_authenticated:
        if
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')
"""
#EndHaytham
