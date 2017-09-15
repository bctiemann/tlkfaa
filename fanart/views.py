from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart.models import Contest, Favorite

import logging
logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_contest'] = Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()
#        context['favorite_artists'] = Favorite.objects.for_user(self.request.user)
        return context


class ArtistsView(TemplateView):
    template_name = 'fanart/artists.html'


class ArtworkView(TemplateView):
    template_name = 'fanart/artwork.html'


class CharactersView(TemplateView):
    template_name = 'fanart/characters.html'


class TradingTreeView(TemplateView):
    template_name = 'fanart/tradingtree.html'


class ColoringCaveView(TemplateView):
    template_name = 'fanart/coloringcave.html'


class SpecialFeaturesView(TemplateView):
    template_name = 'fanart/special.html'


class UserBoxSetView(APIView):

    def get(self, request, box=None, show=None):
        response = {}
        if box in ('favorite_artists', 'favorite_pictures',):
            request.session[box] = True if show == '1' else False
        return Response(response)


class FavoriteArtistsBoxView(TemplateView):
    template_name = 'fanart/userpane/favorite_artists.html'

    def get_context_data(self, **kwargs):
        context = super(FavoriteArtistsBoxView, self).get_context_data(**kwargs)
#        context['favorite_artists'] = Favorite.objects.for_user(self.request.user)
        return context
