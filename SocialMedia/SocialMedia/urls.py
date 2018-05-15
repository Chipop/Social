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

    path('profil/editInterface/', views.editInterface, name="editInterface"),

    path('profil/edit-about/', views.editAbout, name="editAbout"),

    path('profil/edit-experience/<int:pk>/', views.editExperience, name="editExperience"),

    path('profil/edit-formation/<int:pk>/', views.editFormation, name="editFormation"),

    path('home/', views.home, name="home"),

    path('', views.home, name="home"),

    ##Chipop
    path('search_members/', views.search_members, name="search_members"),
    path('search_offers/', views.search_offres, name="search_offres"),
    path('search_groupes/', views.search_groupes, name="search_groupes"),
    path('search/', views.search, name="search"),

    path('test',views.test,name="test"),
    path('profil/ajouterLangue/', views.ajouterLangue, name="ajouterLangue"),
    path('profil/modifierLangue/', views.modifierLangue, name="modifierLangue"),
    path('profil/supprimerLangue/', views.supprimerLangue, name="supprimerLangue"),
    path('profil/getModifierLangue/', views.getModifierLangue, name="getModifierLangue"),

    ##Haytham

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
