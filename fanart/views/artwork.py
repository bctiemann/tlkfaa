import logging
import random
from datetime import timedelta

from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count

from fanart.views import UserPaneMixin
from fanart.models import Picture, UnviewedPicture, Tag
from fanart.utils import PagesLink

logger = logging.getLogger(__name__)


class ArtworkMixin:

    @property
    def recent_upload_cutoff_date(self):
        return timezone.now() - timedelta(days=settings.RECENT_UPLOAD_CUTOFF_DAYS)

    def get_artwork(self):
        artwork = Picture.objects.filter(artist__is_active=True, artist__is_artist=True, artist__num_pictures__gt=0)

        if self.request.user.is_authenticated:
            artwork = artwork.exclude(artist__in=self.request.user.blocked_artists)

        return artwork


class ArtworkView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artwork.html'
    list_type = settings.DEFAULT_ARTWORK_VIEW

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_type'] = self.list_type
        try:
            context['start'] = int(self.request.GET.get('start', 0))
        except ValueError:
            context['start'] = 0
        try:
            context['count'] = int(self.request.GET.get('count', settings.ARTWORK_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTWORK_PER_PAGE
        context['per_page'] = settings.ARTWORK_PER_PAGE
        # For search view
        context['term'] = self.request.GET.get('term', '')
        return context


class ArtworkListView(ArtworkMixin, TemplateView):
    """
    Base view for infinite-scroll/"more" pages loaded asynchronously. This view is subclassed for each
    of the view modes/list types.
    """
    template_name = 'includes/artwork-list.html'
    list_type = settings.DEFAULT_ARTWORK_VIEW

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Overriden in each subclass
        artwork = self.get_artwork()

        start = int(self.request.GET.get('start', 0))

        context['show_search_input'] = False
        context['list_type'] = self.list_type
        context['per_page'] = settings.ARTWORK_PER_PAGE
        try:
            context['count'] = int(self.request.GET.get('count', settings.ARTWORK_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTWORK_PER_PAGE
        context['next_start'] = start + settings.ARTWORK_PER_PAGE
        context['artwork'] = artwork[start:start + context['count']]

        return context


class ArtworkListByNewestView(ArtworkListView):
    list_type = 'newest'

    def get_artwork(self):
        artwork = super().get_artwork()
        return artwork.filter(date_uploaded__gt=self.recent_upload_cutoff_date).order_by('-date_uploaded')


class ArtworkListByUnviewedView(ArtworkListView):
    list_type = 'unviewed'

    def get_artwork(self):
        if not self.request.user.is_authenticated:
            return Picture.objects.none()
        unviewed_pictures = UnviewedPicture.objects.filter(user=self.request.user)
        unviewed_pictures = unviewed_pictures.order_by('-picture__date_uploaded')
        return [uvp.picture for uvp in unviewed_pictures]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For "unviewed" view, each UnviewedPicture is deleted upon viewing, so we pull the next page
        # starting from 0
        context['next_start'] = 0
        return context


class ArtworkListByNewestByFavesView(ArtworkListView):
    list_type = 'newest_by_faves'

    def get_artwork(self):
        if not self.request.user.is_authenticated:
            return Picture.objects.none()

        artwork = super().get_artwork()
        favorite_artists = Subquery(self.request.user.favorite_set.filter(picture__isnull=True).values('artist_id'))
        artwork = artwork.filter(date_uploaded__gt=self.recent_upload_cutoff_date, artist__in=favorite_artists)
        return artwork.order_by('-date_uploaded')


class ArtworkListByTopRatedView(ArtworkListView):
    list_type = 'top_rated'

    def get_artwork(self):
        artwork = super().get_artwork()
        return artwork.filter(num_faves__gt=settings.ARTWORK_TOP_RATED_FAVE_CUTOFF).order_by('-num_faves')


class ArtworkListByTopRatedRecentView(ArtworkListView):
    list_type = 'top_rated_recent'

    def get_artwork(self):
        artwork = super().get_artwork()
        return artwork.filter(date_uploaded__gt=self.recent_upload_cutoff_date).order_by('-num_faves')


class ArtworkListByRandomView(ArtworkListView):
    list_type = 'random'

    def get_artwork(self):
        artwork = super().get_artwork()
        min_id = Picture.objects.all().aggregate(Min('id'))['id__min']
        max_id = Picture.objects.all().aggregate(Max('id'))['id__max']
        rand_range = min(max_id - min_id, 100)
        random_ids = random.sample(list(range(min_id, max_id)), rand_range)
        return artwork.filter(pk__in=random_ids).order_by('?')


# Base class for all three "search" list views: term (in title), tag, and character.
class ArtworkListSearchView(ArtworkListView):
    term = None
    start = None
    year_from = None
    year_to = None

    def dispatch(self, request, *args, **kwargs):
        self.term = request.GET.get('term', None)
        self.start = int(request.GET.get('start', 0))
        self.year_from = request.GET.get('year_from')
        self.year_to = request.GET.get('year_to')
        return super().dispatch(request, *args, **kwargs)

    def get_artwork(self):
        artwork = super().get_artwork()
        current_year = timezone.now().year
        if self.year_from and self.year_from.isnumeric() and current_year >= int(self.year_from) > 0:
            artwork = artwork.filter(date_uploaded__year__gte=self.year_from)
        if self.year_to and self.year_to.isnumeric() and current_year >= int(self.year_to) > 0:
            artwork = artwork.filter(date_uploaded__year__lte=self.year_to)
        return artwork

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_search_input'] = self.start == 0
        context['term'] = self.term
        if not self.term:
            context['top_300_tags'] = sorted(
                Tag.objects.annotate(num_pictures=Count('picture')).order_by('-num_pictures')[:300],
                key=lambda tag: tag.num_pictures, reverse=True
            )
        context['year_from'] = self.year_from
        context['year_to'] = self.year_to
        return context


class ArtworkListSearchByTermView(ArtworkListSearchView):
    list_type = 'search'

    def get_artwork(self):
        artwork = super().get_artwork()
        if not self.term:
            return artwork.none()
        artwork = artwork.filter(title__icontains=self.term).order_by('-num_faves')
        logger.info('Artwork title search by {0} {1}: {2} ({3})'.format(
            self.request.user, self.request.META['REMOTE_ADDR'], self.term, self.start
        ))
        return artwork


class ArtworkListSearchByTagView(ArtworkListSearchView):
    list_type = 'tag'

    def get_artwork(self):
        artwork = super().get_artwork()
        logger.info('Artwork tag search by {0} {1}: {2} ({3})'.format(
            self.request.user, self.request.META['REMOTE_ADDR'], self.term, self.start))
        tag = Tag.objects.filter(tag=self.term).first()
        if tag:
            artwork = tag.picture_set.filter(
                artist__is_active=True,
                artist__is_artist=True,
                artist__num_pictures__gt=0,
            ).order_by('-num_faves')
        else:
            artwork = artwork.filter(id__isnull=True)
        return artwork


# Is this used anywhere? Search artwork by character may only be via the Characters tab now
class ArtworkListSearchByCharacterView(ArtworkListSearchView):
    list_type = 'character'

    def get_artwork(self):
        artwork = super().get_artwork()
        for character_id in self.term.split(','):
            try:
                character_pictures = artwork.filter(picturecharacter__character_id=character_id)
            except ValueError:
                character_pictures = artwork.none()
            artwork = character_pictures.order_by('-picturecharacter__date_tagged')
        return artwork
