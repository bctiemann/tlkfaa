import logging
import random
from datetime import timedelta

from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count

from fanart.views import UserPaneMixin
from fanart.models import Character, User
from fanart.utils import PagesLink

logger = logging.getLogger(__name__)


class CharactersMixin:

    def get_characters(self):
        return Character.objects.all()


class CharactersView(UserPaneMixin, TemplateView):
    template_name = 'fanart/characters.html'
    list_type = settings.DEFAULT_CHARACTERS_VIEW
    tab_selected = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_type'] = self.list_type
        context['tab_selected'] = self.tab_selected or self.list_type
        context['start'] = int(self.request.GET.get('start', 0))
        try:
            context['count'] = int(self.request.GET.get('count', settings.CHARACTERS_PER_PAGE))
        except ValueError:
            context['count'] = settings.CHARACTERS_PER_PAGE
        context['per_page'] = settings.CHARACTERS_PER_PAGE

        # For by-artist view
        dir_name = kwargs.get('dir_name')
        if dir_name:
            context['artist'] = get_object_or_404(User, is_artist=True, dir_name=dir_name)

        # For search view
        context['term'] = self.request.GET.get('term', '')
        return context


class CharactersOldView(UserPaneMixin, TemplateView):
    template_name = 'fanart/characters.html'

    def get_context_data(self, **kwargs):
        context = super(CharactersView, self).get_context_data(**kwargs)

        default_characters_view = settings.DEFAULT_CHARACTERS_VIEW

        dir_name = kwargs.get('dir_name', self.request.GET.get('dir_name', None))
        term = self.request.GET.get('term', None)
        sub_list_type = ''
        match_type = self.request.GET.get('match', 'contains')
        if dir_name:
            context['artist'] = get_object_or_404(models.User, is_artist=True, dir_name=dir_name)
            list_type = 'artist'
        else:
            list_type = kwargs.get('list', self.request.GET.get('list', default_characters_view))
            if not list_type in models.characters_tabs and not dir_name:
                list_type = default_characters_view
            if list_type == 'artist':
                if not term or not term.isnumeric():
                    raise Http404
                context['artist'] = get_object_or_404(models.User, is_artist=True, pk=term)

        mode = list_type
        tab_selected = list_type

        try:
            start = int(self.request.GET.get('start', 0))
        except ValueError:
            start = 0
        initial = self.request.GET.get('initial', None)

        characters = models.Character.objects.all()
        if list_type == 'artist':
            characters = characters.filter(owner=context['artist']).order_by('name')
            tab_selected = 'search'
        elif list_type == 'canon':
            characters = characters.filter(is_canon=True).order_by('-num_pictures')
        elif list_type == 'newest':
            characters = characters.order_by('-date_created')
        elif list_type == 'mosttagged':
            characters = characters.filter(num_pictures__gt=0).order_by('-num_pictures')
        elif list_type == 'recentlytagged':
            characters = characters.filter(num_pictures__gt=0).order_by('-date_tagged')
        elif list_type == 'search':
            context['show_search_box'] = True
            if term:
#                if match_type == 'exact':
#                    characters = characters.filter(species=term)
#                else:
#                    characters = characters.filter(species__icontains=term)
                sub_list_type = self.request.GET.get('list', None)
                logger.info('Character search ({0}): {1}'.format(list_type, term))
                if sub_list_type not in ['artist', 'species', 'charactername']:
                    sub_list_type = 'species'
                characters = characters.filter(owner__is_active=True).order_by('name')
                if sub_list_type == 'artist':
                    try:
                        characters = characters.filter(owner__id=term)
                        context['artist'] = get_object_or_404(models.User, is_artist=True, pk=term)
                    except ValueError:
                        pass
                elif sub_list_type == 'species':
                    if match_type == 'exact':
                        characters = characters.filter(species=term)
                    else:
                        characters = characters.filter(species__icontains=term)
                elif sub_list_type == 'charactername':
                    if match_type == 'exact':
                        characters = characters.filter(name=term)
                    else:
                        characters = characters.filter(name__icontains=term)
                if start > 1:
                    context['show_search_box'] = False
                context['term'] = term
            else:
                characters = characters.filter(id__isnull=True)

#        context['characters_paginator'] = Paginator(characters, settings.CHARACTERS_PER_PAGE)
#        try:
#            page = int(self.request.GET.get('page', 1))
#        except ValueError:
#            page = 1
#        try:
#            characters_page = context['characters_paginator'].page(page)
#        except EmptyPage:
#            characters_page = context['characters_paginator'].page(1)


        context['start'] = start

        context['list_type'] = list_type
        context['sub_list_type'] = sub_list_type
        context['tab_selected'] = tab_selected
        context['per_page'] = settings.CHARACTERS_PER_PAGE
#        context['characters'] = characters_page
#        context['pages_link'] = utils.PagesLink(len(characters), settings.CHARACTERS_PER_PAGE, characters_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        context['count'] = int(self.request.GET.get('count', settings.CHARACTERS_PER_PAGE))
        context['next_start'] = start + settings.CHARACTERS_PER_PAGE
        context['initial'] = initial
        context['match_type'] = match_type
        context['characters'] = characters[start:start + context['count']]

        return context


class CharactersListView(CharactersMixin, TemplateView):
    """
    Base view for infinite-scroll/"more" pages loaded asynchronously. This view is subclassed for each
    of the view modes/list types.
    """
    template_name = 'includes/characters-list.html'
    list_type = settings.DEFAULT_ARTWORK_VIEW

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Overriden in each subclass
        characters = self.get_characters()

        start = int(self.request.GET.get('start', 0))

        context['show_search_input'] = False
        context['list_type'] = self.list_type
        context['per_page'] = settings.CHARACTERS_PER_PAGE
        try:
            context['count'] = int(self.request.GET.get('count', settings.CHARACTERS_PER_PAGE))
        except ValueError:
            context['count'] = settings.CHARACTERS_PER_PAGE
        context['next_start'] = start + settings.CHARACTERS_PER_PAGE
        context['characters'] = characters[start:start + context['count']]

        return context


class CharactersListByCanonView(CharactersListView):
    list_type = 'canon'

    def get_characters(self):
        characters = super().get_characters()
        return characters.filter(is_canon=True).order_by('-num_pictures')


class CharactersListByArtistView(CharactersListView):
    list_type = 'artist'
    artist = None

    def get(self, request, *args, **kwargs):
        dir_name = request.GET.get('dir_name')
        self.artist = get_object_or_404(User, is_artist=True, dir_name=dir_name)
        return super().get(request, *args, **kwargs)

    def get_characters(self):
        characters = super().get_characters()
        return characters.filter(owner=self.artist).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artist'] = self.artist
        return context
