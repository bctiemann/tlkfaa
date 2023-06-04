import logging

from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from fanart.views import UserPaneMixin
from fanart.models import Character, User

logger = logging.getLogger(__name__)


class CharactersMixin:

    def get_characters(self):
        return Character.objects.all()


class CharactersView(UserPaneMixin, TemplateView):
    template_name = 'fanart/characters.html'
    list_type = settings.DEFAULT_CHARACTERS_VIEW
    sub_list_type = 'search'
    term = None
    match_type = None
    tab_selected = None

    def dispatch(self, request, *args, **kwargs):
        self.term = request.GET.get('term', None)
        self.sub_list_type = request.GET.get('list', 'species')
        self.match_type = request.GET.get('match', 'exact')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_type'] = self.list_type
        context['sub_list_type'] = self.sub_list_type
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
        context['match_type'] = self.request.GET.get('match', 'contains')

        return context


class CharactersListView(CharactersMixin, TemplateView):
    """
    Base view for infinite-scroll/"more" pages loaded asynchronously. This view is subclassed for each
    of the view modes/list types.
    """
    template_name = 'includes/characters-list.html'
    list_type = settings.DEFAULT_ARTWORK_VIEW
    sub_list_type = None
    start = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Overriden in each subclass
        characters = self.get_characters()

        self.start = int(self.request.GET.get('start', 0))

        context['show_search_box'] = False
        context['list_type'] = self.list_type
        context['sub_list_type'] = self.sub_list_type
        context['per_page'] = settings.CHARACTERS_PER_PAGE
        try:
            context['count'] = int(self.request.GET.get('count', settings.CHARACTERS_PER_PAGE))
        except ValueError:
            context['count'] = settings.CHARACTERS_PER_PAGE
        context['next_start'] = self.start + settings.CHARACTERS_PER_PAGE
        context['characters'] = characters[self.start:self.start + context['count']]

        return context


class CharactersListByCanonView(CharactersListView):
    list_type = 'canon'

    def get_characters(self):
        characters = super().get_characters()
        return characters.filter(is_canon=True).order_by('-num_pictures')


class CharactersListByNewestView(CharactersListView):
    list_type = 'newest'

    def get_characters(self):
        characters = super().get_characters()
        return characters.order_by('-date_created')


class CharactersListByMostTaggedView(CharactersListView):
    list_type = 'most_tagged'

    def get_characters(self):
        characters = super().get_characters()
        return characters.filter(num_pictures__gt=0).order_by('-num_pictures')


class CharactersListByRecentlyTaggedView(CharactersListView):
    list_type = 'recently_tagged'

    def get_characters(self):
        characters = super().get_characters()
        return characters.filter(num_pictures__gt=0).order_by('-date_tagged')


class CharactersListSearchView(CharactersListView):
    list_type = 'search'
    match_type = None
    term = None

    def dispatch(self, request, *args, **kwargs):
        self.term = request.GET.get('term', None)
        self.sub_list_type = request.GET.get('list', 'species')
        self.match_type = request.GET.get('match', 'exact')
        return super().dispatch(request, *args, **kwargs)

    # TODO: Further factor sub_list_type handling into Search subclasses (see CharactersListSearchBySpeciesView)
    def get_characters(self):
        characters = super().get_characters()
        if not self.term:
            return Character.objects.none()

        if self.sub_list_type == 'artist':
            try:
                characters = characters.filter(owner__id=self.term)
            except ValueError:
                pass

        elif self.sub_list_type == 'species':
            if self.match_type == 'exact':
                characters = characters.filter(species=self.term)
            else:
                characters = characters.filter(species__icontains=self.term)

        elif self.sub_list_type == 'charactername':
            if self.match_type == 'exact':
                characters = characters.filter(name=self.term)
            else:
                characters = characters.filter(name__icontains=self.term)

        return characters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['term'] = self.term
        context['match_type'] = self.match_type
        context['show_search_box'] = not self.term
        return context


# TODO: This refactor requires a JS rework, to handle parameterized URL paths rather than query strings.
class CharactersListSearchBySpeciesView(CharactersListSearchView):
    sub_list_type = 'species'

    def get_characters(self):
        characters = super().get_characters()
        if self.match_type == 'exact':
            return characters.filter(species=self.term)
        return characters.filter(species__icontains=self.term)


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
