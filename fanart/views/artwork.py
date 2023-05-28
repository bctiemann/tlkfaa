import logging
from datetime import timedelta

from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count

from fanart.views import UserPaneMixin
from fanart.models import Picture, UnviewedPicture
from fanart.utils import PagesLink

logger = logging.getLogger(__name__)


class ArtworkMixin:

    @property
    def recent_cutoff_date(self):
        return timezone.now() - timedelta(days=settings.ARTWORK_RECENT_CUTOFF_DAYS)

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
            context['count'] = int(self.request.GET.get('count', settings.ARTWORK_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTWORK_PER_PAGE
        context['per_page'] = settings.ARTWORK_PER_PAGE
        # For search view
        context['term'] = self.request.GET.get('term', '')
        return context


class ArtworkOldView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artwork.html'

    def get_context_data(self, **kwargs):
        context = super(ArtworkView, self).get_context_data(**kwargs)

        context['show_search_input'] = False

        default_artwork_view = settings.DEFAULT_ARTWORK_VIEW
        if self.request.user.is_authenticated and self.request.user.unviewedpicture_set.exists():
            default_artwork_view = 'unviewed'

#        mode = kwargs.get('mode', None)
#        if not mode in ['canon', 'fan', 'mosttagged', 'recentlytagged', 'charactername'] and not dir_name:
#            mode = 'canon'

        list_type = kwargs.get('list', self.request.GET.get('list', default_artwork_view))
        if not list_type in models.artwork_tabs:
            list_type = default_artwork_view

        try:
            start = int(self.request.GET.get('start', 0))
        except ValueError:
            start = 0
        try:
            initial = self.request.GET.get('initial', None)
        except ValueError:
            initial = None

        artwork = models.Picture.objects.filter(artist__is_active=True, artist__is_artist=True, artist__num_pictures__gt=0)

        if self.request.user.is_authenticated:
            artwork = artwork.exclude(artist__in=self.request.user.blocked_artists)

        three_months_ago = timezone.now() - timedelta(days=THREE_MONTHS)
        one_month_ago = timezone.now() - timedelta(days=ONE_MONTH)
        if list_type == 'unviewed' and self.request.user.is_authenticated:
            artwork = [uvp.picture for uvp in models.UnviewedPicture.objects.filter(user=self.request.user).order_by('-picture__date_uploaded')]
        elif list_type == 'newest':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago).order_by('-date_uploaded')
        elif list_type == 'newestfaves' and self.request.user.is_authenticated:
            artwork = artwork.filter(date_uploaded__gt=three_months_ago, artist__in=Subquery(self.request.user.favorite_set.filter(picture__isnull=True).values('artist_id'))).order_by('-date_uploaded')
        elif list_type == 'toprated':
            artwork = artwork.filter(num_faves__gt=100).order_by('-num_faves')
        elif list_type == 'topratedrecent':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago).order_by('-num_faves')
        elif list_type == 'random':
            random_ids = random.sample(list(range(models.Picture.objects.all().aggregate(Min('id'))['id__min'], models.Picture.objects.all().aggregate(Max('id'))['id__max'])), 100)
            artwork = artwork.filter(pk__in=random_ids)
        elif list_type in ['search', 'tag', 'character']:
            term = self.request.GET.get('term', None)
            year_from = self.request.GET.get('year_from')
            year_to = self.request.GET.get('year_to')
            current_year = timezone.now().year
            if year_from and year_from.isnumeric() and current_year >= int(year_from) > 0:
                artwork = artwork.filter(date_uploaded__year__gte=year_from)
                context['year_from'] = year_from
            if year_to and year_to.isnumeric() and current_year >= int(year_to) > 0:
                artwork = artwork.filter(date_uploaded__year__lte=year_to)
                context['year_to'] = year_to
            if not term:
                context['show_search_input'] = True
                context['top_300_tags'] = sorted(models.Tag.objects.annotate(num_pictures=Count('picture')).order_by('-num_pictures')[:300], key=lambda tag: tag.num_pictures, reverse=True)
            if term:
                if start == 0:
                    context['show_search_input'] = True
                context['term'] = term
                if list_type == 'search':
                    artwork = artwork.filter(title__icontains=term).order_by('-num_faves')
                    logger.info('Artwork title search by {0} {1}: {2} ({3})'.format(self.request.user, self.request.META['REMOTE_ADDR'], term, start))
                elif list_type == 'tag':
                    logger.info('Artwork tag search by {0} {1}: {2} ({3})'.format(self.request.user, self.request.META['REMOTE_ADDR'], term, start))
                    tag = models.Tag.objects.filter(tag=term).first()
                    if tag:
                        artwork = tag.picture_set.filter(artist__is_active=True, artist__is_artist=True, artist__num_pictures__gt=0).order_by('-num_faves')
                    else:
                        artwork = artwork.filter(id__isnull=True)
                elif list_type == 'character':
                    character_pictures = models.Picture.objects.all()
                    for character_id in term.split(','):
                        try:
                            character_pictures = character_pictures.filter(picturecharacter__character_id=character_id)
                        except ValueError:
                            character_pictures = character_pictures.none()
                        artwork = character_pictures.order_by('-picturecharacter__date_tagged')
            else:
                artwork = artwork.filter(id__isnull=True)

        context['list_type'] = list_type
        context['per_page'] = settings.ARTWORK_PER_PAGE
        try:
            context['count'] = int(self.request.GET.get('count', settings.ARTWORK_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTWORK_PER_PAGE
        context['next_start'] = start + settings.ARTWORK_PER_PAGE
        context['initial'] = initial
        context['artwork'] = artwork[start:start + context['count']]

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
        return artwork.filter(date_uploaded__gt=self.recent_cutoff_date).order_by('-date_uploaded')


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
        context['next_start'] = 0
        return context


class ArtworkListByNewestByFaves(ArtworkListView):
    list_type = 'newest_by_faves'

    def get_artwork(self):
        if not self.request.user.is_authenticated:
            return Picture.objects.none()

        artwork = super().get_artwork()
        recent_upload_cutoff = timezone.now() - timedelta(days=settings.RECENT_UPLOAD_CUTOFF_DAYS)
        favorite_artists = Subquery(self.request.user.favorite_set.filter(picture__isnull=True).values('artist_id'))
        artwork = artwork.filter(date_uploaded__gt=recent_upload_cutoff, artist__in=favorite_artists)
        return artwork.order_by('-date_uploaded')
