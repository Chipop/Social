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


# Create your views here.


def home(request):
    return render(request, 'SocialMedia/acceuil.html')


def profil(request):
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        if p.is_first_socialmedia:
            p.is_first_socialmedia = False
            p.save()
        profiles = Profil.objects.filter(user__is_superuser=True)
        photoform = PhotoForm()
        return render(request, 'SocialMedia/profil/profil.html',
                      {'profiles': profiles, 'photoform': photoform, 'is_first': p.is_first_socialmedia})
    else:
        messages.error(request, "Il faut être connecté pour accéder à cette page!")
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
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
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
        context = {'statut': True,
                   'username': p.user.username,
                   'last_login': last_login,
                   'photo_profil': p.photo_profil.image.url
                   }
        return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


def groupesProfil(request):
    if request.user.is_authenticated:
        formDemande = demandeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            demande = DemandeAmi.objects.get(id=formDemande.cleaned_data['demande'])
            demande.statut = formDemande.cleaned_data['statut']
            demande.save()
            if formDemande.cleaned_data['statut'] == 1:
                context = {'statut': demande.statut,
                           'ami': demande.emetteur.user.username,
                           'demande': demande.id,
                           'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
                           }
                return JsonResponse(context, safe=False)
            elif formDemande.cleaned_data['statut'] == 2:
                context = {'statut': demande.statut,
                           'ami': demande.emetteur.user.username,
                           'demande': demande.id,
                           'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
                           }
                return JsonResponse(context, safe=False)
            elif formDemande.cleaned_data['statut'] == 3:
                context = {'statut': demande.statut,
                           'ami': demande.emetteur.user.username,
                           'demande': demande.id,
                           'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
                           }
                return JsonResponse(context, safe=False)
        else:
            demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0)
            photoform = PhotoForm()
            return render(request, 'SocialMedia/profil/demandesProfil.html',
                          {'demandesAmis': demandesAmis, 'photoform': photoform, 'formDemande': formDemande})
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')


def demandes(request):
    if request.user.is_authenticated:
        formDemande = demandeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            demande = DemandeAmi.objects.get(id=formDemande.cleaned_data['demande'])
            demande.statut = formDemande.cleaned_data['statut']
            demande.save()
            demandesAmis = list(DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).values())
            context = {'statut': demande.statut,
                       'ami': demande.emetteur.user.username,
                       'demande': demande.id,
                       'nbdemandes': DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count(),
                       'demandesAmis': demandesAmis,
                       }
            return JsonResponse(context, safe=False)
        else:
            demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id')
            paginator = Paginator(demandesAmis, 3)  # Show 3 Profiles per page
            page = request.GET.get('page')
            demAmis = paginator.get_page(page)
            photoform = PhotoForm()
            return render(request, 'SocialMedia/profil/demandesProfil.html',
                          {'demandesAmis': demAmis, 'photoform': photoform, 'formDemande': formDemande})
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
        'nbdemandes': len(demAmis),
        'NumPagesExcessed': isNumPagesExcessed,
    }
    return JsonResponse(context, safe=False)


def getProfil(request, id):
    pass


def suprimerAmi(request):
    pass


def findfriends(request):
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        friends_and_requests = DemandeAmi.objects.exclude(emetteur=request.user, )
        profiles = Profil.objects.all()
        return render(request, 'SocialMedia/profil/demandesProfil.html', {'profiles': profiles})
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('SocialMedia:login')


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


def supprimerDemande(request):
    pass


def getProfil(request, id):
    pass


def suprimerAmi(request):
    pass


def chat(request):
    pass


def rechercherAmis(request):
    pass


def search(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404

    # Contacts Search
    profils = Profil.objects.filter(Q(user__last_name__contains=keywords) | Q(user__first_name__contains=keywords),
                                    user__is_active=True).exclude(id = request.user.profil.id)

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
                                         user__is_active=True).exclude(id = request.user.profil.id)

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
    offres_list = OffreEmploi.objects.filter(Q(type_contrat__contains=keywords) | Q(diplome_requis__contains=keywords) | Q(
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
