from datetime import timedelta

from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage

from fanart.views import UserPaneMixin
from fanart.models import User
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
    list_type = settings.DEFAULT_ARTISTS_VIEW

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_type'] = self.list_type
        try:
            context['start'] = int(self.request.GET.get('start', 0))
        except ValueError:
            context['start'] = 0
        try:
            context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTISTS_PER_PAGE
        context['per_page'] = settings.ARTISTS_PER_PAGE
        # For search view
        context['term'] = self.request.GET.get('term', '')
        return context


class ArtistsByNameView(ArtistsMixin, ArtistsView):
    """
    "Initial" based artist pages are rendered inline with a paginator; no "more" button or infinite scroll.
    This means there is also no ArtistsListByNameView.
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
    list_type = settings.DEFAULT_ARTISTS_VIEW

    @property
    def recent_upload_cutoff_date(self):
        return timezone.now() - timedelta(days=settings.RECENT_UPLOAD_CUTOFF_DAYS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Overriden in each subclass
        artists = self.get_artists()

        start = int(self.request.GET.get('start', 0))

        context['show_search_input'] = False
        context['list_type'] = self.list_type
        context['per_page'] = settings.ARTISTS_PER_PAGE
        try:
            context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTISTS_PER_PAGE
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['artists'] = artists[start:start + context['count']]

        return context


class ArtistsListByNewestView(ArtistsListView):
    list_type = 'newest'

    def get_artists(self):
        artists = super().get_artists()
        return artists.order_by('-date_joined')


class ArtistsListByRecentlyActiveView(ArtistsListView):
    list_type = 'recently_active'

    def get_artists(self):
        artists = super().get_artists()
        return artists.order_by('-last_upload')


class ArtistsListByTopRatedView(ArtistsListView):
    list_type = 'top_rated'

    def get_artists(self):
        artists = super().get_artists()
        return artists.extra(
            select={'rating': 'num_favepics / num_pictures * num_faves'}
        ).order_by('-rating')


class ArtistsListByTopRatedActiveView(ArtistsListView):
    list_type = 'top_rated_active'

    def get_artists(self):
        artists = super().get_artists()
        return artists.filter(last_upload__gt=self.recent_upload_cutoff_date).extra(
            select={'rating': 'num_favepics / num_pictures * num_faves'}
        ).order_by('-rating')


class ArtistsListByMostProlificView(ArtistsListView):
    list_type = 'most_prolific'

    def get_artists(self):
        artists = super().get_artists()
        return artists.order_by('-num_pictures')


class ArtistsListByRandomView(ArtistsListView):
    list_type = 'random'

    def get_artists(self):
        artists = super().get_artists()
        return artists.order_by('?')


class ArtistsListBySearchView(ArtistsListView):
    list_type = 'search'

    @property
    def term(self):
        return self.request.GET.get('term', None)

    def get_artists(self):
        artists = super().get_artists()
        if self.term:
            artists = artists.filter(username__icontains=self.term).order_by('sort_name')
        else:
            artists = artists.filter(id__isnull=True)
        return artists

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.term:
            context['term'] = self.term
        else:
            context['show_search_input'] = True
        return context
