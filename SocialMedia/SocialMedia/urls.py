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
<<<<<<< HEAD
    path('profil/ajouterLangue/', views.ajouterLangue, name="ajouterLangue"),
    path('profil/modifierLangue/', views.modifierLangue, name="modifierLangue"),
    path('profil/supprimerLangue/', views.supprimerLangue, name="supprimerLangue"),
    path('profil/getModifierLangue/', views.getModifierLangue, name="getModifierLangue"),

    ##Haytham
=======
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
>>>>>>> d5a4491f9b709cb18afa2f9d6a528df99ed6be21

    path('profil/<int:pk>/follow', views.followProfil, name="followProfil"),

    path('profil/<int:pk>/reponse-ami', views.FriendsRequests, name="addFriend"),

    path('profil/<int:pk>/get-responses-updates', views.getRequestsUpdates, name="getUpdates"),

    path('profil/<int:pk>', views.getProfil, name='getProfil'),

    path('profil/<int:pk>/groupes', views.getProfilGroupes, name='getProfilGroupes'),

    path('groupe/<int:pk>/', views.groupe, name="groupe"),

    path('groupe/<int:pk>/demandes/', views.demandesGroupe, name="demandesGroupe"),

    path('groupe/<int:pk>/ajax-demandes-groupe/', views.demandesGroupeViaAjax, name="demandesGroupeViaAjax"),

    path('groupe/<int:pk>/membres/', views.membresGroupe, name="membresGroupe"),

    path('groupe/<int:pk>/ajax-members-groupe', views.membersGroupeViaAjax, name="membresGroupeViaAjax"),

    path('groupe/<int:pk>/joinGroupeViaAjax', views.joinGroupeViaAjax, name="joinGroupeViaAjax"),

    path('groupe/<int:pk>/more-comments', views.getMoreComments, name="getMoreComments"),

    path('groupe/<int:pk>/change-photo-couverture-groupe', views.changephotocouverturegroupe, name="changephotocouverturegroupe"),

    path('groupe/<int:pk>/change-photo-profil-groupe', views.changephotoprofilgroupe, name="changephotoprofilgroupe"),







]
