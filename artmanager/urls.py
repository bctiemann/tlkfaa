from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import RedirectView

from artmanager import views as artmanager_views

urlpatterns = [
    url(r'^$', artmanager_views.ArtManagerRedirectView.as_view(), name='home'),
#        RedirectView.as_view(
#            url='dashboard',
#            permanent=False),
#        name='home'
#    ),
    url(r'^dashboard/$', artmanager_views.ArtManagerDashboardView.as_view(), name='dashboard'),
    url(r'^prefs/$', artmanager_views.ArtManagerPrefsView.as_view(), name='prefs'),
]
