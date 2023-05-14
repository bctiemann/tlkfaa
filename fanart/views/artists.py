from datetime import timedelta

from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage

from fanart.views import UserPaneMixin
from fanart.models import artists_tabs, User
from fanart.utils import PagesLink


class ArtistsMixin:

    def get_artists(self):
        artists = User.objects.filter(is_active=True, is_artist=True, num_pictures__gt=0)
        if self.request.user.is_authenticated:
            artists = artists.exclude(id__in=self.request.user.blocked_artist_ids)
        return artists


# This view should just be the TemplateView of artists.html with no content listed in it; it should load
# content asynchronously via JS, and call ArtistsListView or one of its subclasses differentiated by list_type.
class ArtistsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artists/base.html'
    list_type = 'newest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list'] = self.list_type
        context['count'] = settings.ARTISTS_PER_PAGE_INITIAL
        context['per_page'] = settings.ARTISTS_PER_PAGE
        return context


class ArtistsByNameView(ArtistsMixin, ArtistsView):
    """
    "Initial" based artist pages are rendered inline with a paginator; no "more" button or infinite scroll.
    """
    template_name = 'fanart/artists/by_name.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        initial = kwargs['initial']

        artists = self.get_artists()
        artists = artists.filter(username__istartswith=initial).order_by('username')
        artists_paginator = Paginator(artists, settings.ARTISTS_PER_PAGE_INITIAL)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            artists_page = artists_paginator.page(page)
        except EmptyPage:
            artists_page = artists_paginator.page(1)

        context['list'] = 'name'
        context['artists'] = artists_page
        context['count'] = None
        context['pages_link'] = PagesLink(
            items_total=len(artists),
            items_per_page=settings.ARTISTS_PER_PAGE_INITIAL,
            page_num=artists_page.number,
            is_descending=False,
            base_url=self.request.path,
            query_dict=self.request.GET,
        )

        return context


class ArtistsListView(ArtistsMixin, TemplateView):
    """
    Base view for infinite-scroll/"more" pages loaded asynchronously. This view is subclassed for each
    of the view modes/list types.
    """
    template_name = 'includes/artists-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['show_search_input'] = False

        list_type = kwargs.get('list', self.request.GET.get('list', settings.DEFAULT_ARTISTS_VIEW))
        if not list_type in artists_tabs:
            list_type = settings.DEFAULT_ARTISTS_VIEW

        start = int(self.request.GET.get('start', 0))
        initial = self.request.GET.get('initial', None)

        artists = self.get_artists()

        one_month_ago = timezone.now() - timedelta(days=180)
        # if list_type == 'name':
        #     if not initial:
        #         raise Http404
        #
        #     artists = artists.filter(username__istartswith=initial).order_by('username')
        #     context['artists_paginator'] = Paginator(artists, settings.ARTISTS_PER_PAGE_INITIAL)
        #     try:
        #         page = int(self.request.GET.get('page', 1))
        #     except ValueError:
        #         page = 1
        #     try:
        #         artists_page = context['artists_paginator'].page(page)
        #     except EmptyPage:
        #         artists_page = context['artists_paginator'].page(1)
        if list_type == 'newest':
            artists = artists.order_by('-date_joined')
        elif list_type == 'recentactive':
            artists = artists.order_by('-last_upload')
        elif list_type == 'toprated':
            artists = artists.extra(select={'rating': 'num_favepics / num_pictures * num_faves'}).order_by('-rating')
        elif list_type == 'topratedactive':
            artists = artists.filter(last_upload__gt=one_month_ago).extra(select={'rating': 'num_favepics / num_pictures * num_faves'}).order_by('-rating')
        elif list_type == 'prolific':
            artists = artists.order_by('-num_pictures')
        elif list_type == 'random':
            artists = artists.order_by('?')
        elif list_type == 'search':
            term = self.request.GET.get('term', None)
            if not term:
                context['show_search_input'] = True
            if term:
                context['term'] = term
                artists = artists.filter(username__icontains=term).order_by('sort_name')
            else:
                artists = artists.filter(id__isnull=True)

        context['list_type'] = list_type
        context['per_page'] = settings.ARTISTS_PER_PAGE
        context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['initial'] = initial
        context['artists'] = artists[start:start + context['count']]
        # if list_type == 'name':
        #     context['artists'] = artists_page
        #     context['count'] = None
        #     context['pages_link'] = PagesLink(len(artists), settings.ARTISTS_PER_PAGE_INITIAL, artists_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        return context


class ArtistsListByNameView(ArtistsListView):

    def get_artists(self):
        artists = super().get_artists()
        initial = self.request.GET.get('initial', None)
        if not initial:
            raise Http404
        return artists.filter(username__istartswith=initial).order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artists = self.get_artists()
        context['artists_paginator'] = Paginator(artists, settings.ARTISTS_PER_PAGE_INITIAL)

        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            artists_page = context['artists_paginator'].page(page)
        except EmptyPage:
            artists_page = context['artists_paginator'].page(1)

        start = int(self.request.GET.get('start', 0))

        context['artists'] = artists_page
        context['list_type'] = 'name'
        context['per_page'] = settings.ARTISTS_PER_PAGE
        context['count'] = None
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['pages_link'] = PagesLink(len(artists), settings.ARTISTS_PER_PAGE_INITIAL, artists_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)
        context['initial'] = self.request.GET.get('initial', None)

        return context


class ArtistsListByNewestView(ArtistsListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ArtistsListByRecentlyActiveView(ArtistsListView):

    # TODO: Don't show "more" button if there are no more (not necessary? Infinite scrolling)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['show_search_input'] = False

        start = int(self.request.GET.get('start', 0))
        initial = self.request.GET.get('initial', None)

        artists = self.get_artists()
        artists = artists.order_by('-last_upload')

        context['list_type'] = 'recently_active'
        context['per_page'] = settings.ARTISTS_PER_PAGE
        context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['initial'] = initial
        context['artists'] = artists[start:start + context['count']]

        return context
