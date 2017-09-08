from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone

from fanart.models import Contest


class HomeView(TemplateView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_contest'] = Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()
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
