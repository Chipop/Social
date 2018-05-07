from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf.urls.static import settings, static
from . import views

app_name = "SocialMedia"

urlpatterns = [
    path('profil/', views.profil, name='profil'),
    path('ajaxuser/', views.ajaxUser, name="AjaxUser"),
    path('demandes', views.demandes, name="demandes"),
    path('supprimer-ami/', views.suprimerAmi, name="supprimerAmi"),
    url('rechercher-amis', views.rechercherAmis, name="rechercherAmis"),
    url('profil/(?P<pk>\w+)/?$', views.getProfil, name="getProfil"),
    path('chat', views.chat, name="chat"),
    path('uploads', views.uploads.as_view(), name="uploads"),

    path('demandeajax', views.demandeViaAjax, name="demandeViaAjax"),

    path('changephotocouverture', views.changephotocouverture, name="changephotocouverture"),

    path('changephotoprofil', views.changephotoprofil, name="changephotoprofil"),

    path('groupes', views.groupesProfil, name="groupes"),

    path('home/', views.home, name="home"),
    path('', views.home, name="home"),

    ##Chipop
    path('search_members/', views.search_members, name="search_members"),
    path('search_offers/', views.search_offres, name="search_offres"),
    path('search_groupes/', views.search_groupes, name="search_groupes"),
    path('search/', views.search, name="search"),
]
