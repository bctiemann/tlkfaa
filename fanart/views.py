from django.conf import settings
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

from fanart.models import Contest, Favorite, TradingOffer, TradingClaim

from datetime import timedelta

import logging
logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_contest'] = Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()
#        context['favorite_artists'] = Favorite.objects.for_user(self.request.user)
        context['settings'] = settings
        context['sketcher_users'] = range(12)

        icons_publish_start_date = timezone.now() - timedelta(weeks=3)
        context['icons'] = TradingOffer.objects.filter(type='icon', is_active=True, is_visible=True, date_posted__gt=icons_publish_start_date)
        context['icons_today'] = TradingOffer.objects.filter(type='icon', is_active=True, is_visible=True, date_posted__date__gte=timezone.now())
        context['icons_mine'] = TradingClaim.objects.filter(offer__type='icon', offer__is_active=True, offer__is_visible=True, date_fulfilled__isnull=True, filename='', date_posted__gt=icons_publish_start_date, user=self.request.user)

#        SELECT * FROM claims,offers
#        WHERE claims.offerid=offers.offerid
#        AND type='icon'
#        AND active=true
#        AND visible=true
#        AND claims.filename IS NOT NULL
#        AND fulfilled IS NULL
#        AND claims.userid=?
#        AND offers.posted>DATE_SUB(NOW(),INTERVAL 3 WEEK)

#        <sql:query var="qryIconsToday">
#        SELECT * FROM offers
#        WHERE type='icon'
#        AND active=true
#        AND visible=true
#        AND posted>DATE(NOW())
#        </sql:query>

#        SELECT * FROM offers
#        WHERE type='icon'
#        AND active=true
#        AND visible=true
#        AND posted>DATE_SUB(NOW(),INTERVAL 3 WEEK)

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
        if box in ('favorite_artists_box', 'favorite_pictures_box', 'sketcher_box', 'community_art_box', 'contests_box', 'tool_box',):
            request.session[box] = True if show == '1' else False
        return Response(response)


class UserBoxView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(UserBoxView, self).get_context_data(**kwargs)
        context['settings'] = settings
        context['sketcher_users'] = range(12)

        icons_publish_start_date = timezone.now() - timedelta(weeks=3)
        context['icons'] = TradingOffer.objects.filter(type='icon', is_active=True, is_visible=True, date_posted__gt=icons_publish_start_date)

        return context


class FavoriteArtistsBoxView(UserBoxView):
    template_name = 'fanart/userpane/favorite_artists.html'

class FavoritePicturesBoxView(UserBoxView):
    template_name = 'fanart/userpane/favorite_pictures.html'

class SketcherBoxView(UserBoxView):
    template_name = 'fanart/userpane/sketcher.html'

class CommunityArtBoxView(UserBoxView):
    template_name = 'fanart/userpane/community_art.html'

class ContestsBoxView(UserBoxView):
    template_name = 'fanart/userpane/contests.html'

class ToolBoxView(UserBoxView):
    template_name = 'fanart/userpane/toolbox.html'

