from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf.urls.static import settings, static
from . import views

app_name = "SocialMedia"

urlpatterns = [
    path('myprofil/', views.profil, name='myprofil'),
    path('ajaxuser/', views.ajaxUser, name="AjaxUser"),
    path('myprofil/demandes', views.demandesProfil, name="demandes"),
    path('myprofil/media', views.mediaProfil, name="mediaProfil"),
    path('supprimer-ami/', views.suprimerAmi, name="supprimerAmi"),
    url('rechercher-amis', views.rechercherAmis, name="rechercherAmis"),
    path('chat', views.chat, name="chat"),
    path('uploads', views.uploads.as_view(), name="uploads"),
    path('changephotocouverture', views.changephotocouverture, name="changephotocouverture"),

    path('changephotoprofil', views.changephotoprofil, name="changephotoprofil"),

    path('myprofil/groupes', views.groupesProfil, name="groupes"),

    path('demandeajax', views.demandeViaAjax, name="demandeViaAjax"),

    path('myprofil/editInterface/', views.editInterface, name="editInterface"),

    path('myprofil/edit-about/', views.editAbout, name="editAbout"),

    path('myprofil/edit-experience/<int:pk>/', views.editExperience, name="editExperience"),

    path('myprofil/edit-formation/<int:pk>/', views.editFormation, name="editFormation"),

    path('home/', views.home, name="home"),
    path('', views.home, name="home"),

    ##Chipop
    path('search_members/', views.search_members, name="search_members"),
    path('search_offers/', views.search_offres, name="search_offres"),
    path('search_groupes/', views.search_groupes, name="search_groupes"),
    path('search/', views.search, name="search"),

    ##Haytham

    path('myprofil/<int:pk>/follow', views.followProfil, name="followProfil"),

    path('myprofil/<int:pk>/addFriend', views.addFriend, name="addFriend"),

    path('profil/<int:pk>', views.getProfil, name='getProfil'),
]
