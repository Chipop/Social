from django.shortcuts import render, redirect
from main_app.models import *
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta


# Haytham


def home(request):
    return render(request, 'SocialMedia/index.html')

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
        return render(request, 'SocialMedia/profil/profil.html', context)
    else:
        messages.error(request, "Veuiller Se Connecter!")
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
            return redirect("SocialMedia:profil")
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
            return redirect("SocialMedia:profil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")

def ajaxUser(request):
    if request.user.is_authenticated:
        pid = request.GET.get('pid')
        p = Profil.objects.get(id=pid)
        if p.user.last_login is not None:
            last_login = p.user.last_login.strftime("%b. %m, %Y, %I:%M %p")
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
        return redirect('SocialMedia:profil')
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
        return render(request, "main_app/authentification/login.html")

def groupesProfil(request):
    if request.user.is_authenticated:
        formDemande = demandeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            demande = DemandeAmi.objects.get(id=formDemande.cleaned_data['demande'])
            demande.statut = formDemande.cleaned_data['statut']
            demande.save()
            if formDemande.cleaned_data['statut'] == 1:
                context={'statut': demande.statut,
                         'ami':demande.emetteur.user.username,
                         'demande':demande.id,
                         'nbdemandes':DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
                         }
                return JsonResponse(context,safe=False)
            elif formDemande.cleaned_data['statut'] == 2:
                context={'statut': demande.statut,
                         'ami':demande.emetteur.user.username,
                         'demande':demande.id,
                         'nbdemandes':DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
                         }
                return JsonResponse(context,safe=False)
            elif formDemande.cleaned_data['statut'] == 3:
                context={'statut': demande.statut,
                         'ami':demande.emetteur.user.username,
                         'demande':demande.id,
                         'nbdemandes':DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
                         }
                return JsonResponse(context,safe=False)
        else:
            demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0)
            photoform = PhotoForm()
            return render(request, 'SocialMedia/profil/groupesProfil.html', {'demandesAmis': demandesAmis, 'photoform': photoform, 'formDemande':formDemande})
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

def register(request):
    if request.user.is_authenticated:
        return redirect('SocialMedia:profil')
    if request.method == "POST":
        userf = userform(request.POST)
        if userf.is_valid():
            userf.save()
            user = authenticate(username=userf.cleaned_data['username'], password=userf.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                return redirect('SocialMedia:finishregistration')
        else:
            return redirect('SocialMedia:signup')
    else:
        return redirect('main_app:signup')
        #formuser = userform()
        #return render(request, 'main_app/authentification/signup.html', {'formuser':formuser})

def supprimerDemande(request):
    pass

def demandesProfil(request):
    if request.user.is_authenticated:
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
            paginator = Paginator(demandesAmis, 3)  # Show 3 Profiles per page
            page = request.GET.get('page')
            demAmis = paginator.get_page(page)
            photoform = PhotoForm()
            return render(request, 'SocialMedia/profil/demandesProfil.html', {'demandesAmis': demAmis, 'photoform': photoform, 'formDemande':formDemande, "nbdemandes":demandesAmis.count()})
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')

def demandeViaAjax(request):
    demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id').values()
    paginator = Paginator(demandesAmis, 3)  # Show 3 Profiles per page
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
            return render(request, "SocialMedia/profil/mediaProfil.html",)
        else:
            profiles = Profil.objects.all().order_by('-id')[:20]
            photoform = PhotoForm()
            albums = Album.objects.filter(user=request.user)
            for album in albums:
                for file in album.reseausocialfile_set.all():
                    print(file.date_telechargement)
            return render(request, 'SocialMedia/profil/mediaProfil.html',{'profiles': profiles, 'photoform': photoform, 'is_first': request.user.profil.is_first_socialmedia,'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()})
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')





















def suprimerAmi(request):
    pass




def findfriends(request):
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        friends_and_requests = DemandeAmi.objects.exclude(emetteur=request.user, )
        profiles = Profil.objects.all()
        return render(request, 'SocialMedia/profil/demandesProfil.html', {'profiles':profiles})
    else:
        messages.error(request, "Veuiller Se Connecter!")
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
            return render(request, 'SocialMedia/profil/forms/base_forms.html', {'formUserInterface':form})
    else:
        messages.error(request, "Veuiller Se Connecter!")
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
            return render(request, 'SocialMedia/profil/forms/editAboutForm.html', {'editForm':form, 'nom': 'A Propos de', 'entreprises':entreprises})
    else:
        messages.error(request, "Veuiller Se Connecter!")
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
            return redirect('SocialMedia:profil')
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
            return render(request, 'SocialMedia/profil/forms/editExperience.html', {'editForm':form, 'exp':exp.id, 'nom': 'Experience De '})
    else:
        messages.error(request, "Veuiller Se Connecter!")
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
            return redirect('SocialMedia:profil')
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
            return render(request, 'SocialMedia/profil/forms/editFormation.html', {'editForm':form, 'nom': 'A Propos de', 'formation':formation.id, 'postes':ecoles})
    else:
        messages.error(request, "Veuiller Se Connecter!")
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
