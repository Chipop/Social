from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf.urls.static import settings, static
from . import views

app_name = "SocialMedia"

urlpatterns = [
    path('profil/', views.profil, name='myprofil'),
    path('ajaxuser/', views.ajaxUser, name="AjaxUser"),
    path('profil/demandes/', views.demandesProfil, name="demandes"),
    path('profil/media', views.mediaProfil, name="mediaProfil"),
    path('supprimer-ami/', views.suprimerAmi, name="supprimerAmi"),
    url('rechercher-amis', views.rechercherAmis, name="rechercherAmis"),
    #path('chat', views.chat, name="chat"),
    path('uploads', views.uploads.as_view(), name="uploads"),
    path('changephotocouverture', views.changephotocouverture, name="changephotocouverture"),

    path('changephotoprofil', views.changephotoprofil, name="changephotoprofil"),

    path('profil/groupes', views.groupesProfil, name="groupes"),

    path('demandeajax', views.demandeViaAjax, name="demandeViaAjax"),


    path('home/', views.home, name="home"),

    path('', views.home, name="home"),

    ##Chipop
    path('search_members/', views.search_members, name="search_members"),
    path('search_offers/', views.search_offres, name="search_offres"),
    path('search_groupes/', views.search_groupes, name="search_groupes"),
    path('search/', views.search, name="search"),

    path('test',views.test,name="test"),
    #Langue my profil
    path('myprofil/ajouterLangue/', views.ajouterLangue, name="ajouterLangue"),
    path('myprofil/getModifierLangue/', views.getModifierLangue, name="getModifierLangue"),
    path('myprofil/modifierLangue/', views.modifierLangue, name="modifierLangue"),
    path('myprofil/supprimerLangue/', views.supprimerLangue, name="supprimerLangue"),
    #Experience myprofil
    path('myprofil/ajouterExperience/', views.ajouterExperience, name="ajouterExperience"),
    path('myprofil/supprimerExperience/', views.supprimerExperience, name="supprimerExperience"),
    path('myprofil/getModifierExperience/', views.getModifierExperience, name="getModifierExperience"),
    path('myprofil/modifierExperience/', views.modifierExperience, name="modifierExperience"),
    #Formation myprofil
    path('myprofil/ajouterFormation/', views.ajouterFormation, name="ajouterFormation"),
    path('myprofil/supprimerFormation/', views.supprimerFormation, name="supprimerFormation"),
    path('myprofil/getModifierFormation/', views.getModifierFormation, name="getModifierFormation"),
    path('myprofil/modifierFormation/', views.modifierFormation, name="modifierFormation"),
    #Benevolar myprofil
    path('myprofil/ajouterBenevolat/', views.ajouterBenevolat, name="ajouterBenevolat"),
    path('myprofil/supprimerBenevolat/', views.supprimerBenevolat, name="supprimerBenevolat"),
    path('myprofil/getModifierBenevolat/', views.getModifierBenevolat, name="getModifierBenevolat"),
    path('myprofil/modifierBenevolat/', views.modifierBenevolat, name="modifierBenevolat"),
    #Informations myprofil
    path('myprofil/getModifierInformations/', views.getModifierInformations, name="getModifierInformations"),
    path('myprofil/modifierInformations/', views.modifierInformations, name="modifierInformations"),
    #InformationsProfil myprofil
    path('myprofil/getModifierInformationsProfil/', views.getModifierInformationsProfil, name="getModifierInformationsProfil"),
    path('myprofil/modifierInformationsProfil/', views.modifierInformationsProfil, name="modifierInformationsProfil"),
    # Offre d'emplois
    path('creer_offre/', views.creer_offre, name="creer_offre"),
    path('creer_entreprise/', views.creer_entreprise, name="creer_entreprise"),

    #Haytham

    path('profil/<int:pk>/follow', views.followProfil, name="followProfil"),

    path('profil/<int:pk>/reponse-ami', views.FriendsRequests, name="addFriend"),

    path('profil/<int:pk>/get-responses-updates', views.getRequestsUpdates, name="getUpdates"),

    path('profil/<int:pk>', views.getProfil, name='getProfil'),

    path('profil/<int:pk>/groupes', views.getProfilGroupes, name='getProfilGroupes'),

    path('groupe/<int:pk>/', views.groupe, name="groupe"),

    path('groupe/<int:pk>/demandes/', views.demandesGroupe, name="demandesGroupe"),

    path('groupe/<int:pk>/ajax-demandes-groupe/', views.demandesGroupeViaAjax, name="demandesGroupeViaAjax"),
]
