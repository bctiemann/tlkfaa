from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from fanart.views import UserPaneMixin
from fanart.models import Showcase, Contest, FeaturedArtist, FeaturedPicture
from fanart.utils import PagesLink


class ChamberOfStarsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/chamber_of_stars/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contest'] = Contest.objects.filter(type='global', date_start__lt=timezone.now(), is_active=True).order_by('-date_created').first()
        context['contest_entries'] = context['contest'].winning_entries

        context['showcases'] = Showcase.objects.filter(is_visible=True).order_by('id')

        return context


class ShowcasesView(UserPaneMixin, TemplateView):
    template_name = 'fanart/chamber_of_stars/showcases.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contest'] = Contest.objects.filter(type='global', date_start__lt=timezone.now(), is_active=True).order_by('-date_created').first()
        context['contest_entries'] = context['contest'].winning_entries

        context['showcases'] = Showcase.objects.filter(is_visible=True).order_by('id')

        return context


class ShowcaseView(UserPaneMixin, TemplateView):
    template_name = 'fanart/chamber_of_stars/showcase.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['showcase'] = get_object_or_404(Showcase, pk=kwargs['showcase_id'])

        pictures = context['showcase'].pictures.order_by('date_uploaded')
        pictures = pictures.filter(artist__is_active=True)

        context['pictures_paginator'] = Paginator(pictures, settings.PICTURES_PER_PAGE)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        reversed_page = context['pictures_paginator'].num_pages - page + 1

        try:
            context['pictures'] = context['pictures_paginator'].page(reversed_page)
        except EmptyPage:
            context['pictures'] = context['pictures_paginator'].page(context['pictures_paginator'].num_pages)
        context['page_number'] = context['pictures_paginator'].num_pages - context['pictures'].number + 1

        context['pages_link'] = PagesLink(len(pictures), settings.PICTURES_PER_PAGE, context['page_number'], is_descending=True, base_url=self.request.path, query_dict=self.request.GET)

        return context

"""
- Featured Artists of the Month
- Featured Artwork
- Showcases
- Contests
"""


class FeaturedArtistsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/chamber_of_stars/featured_artists.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_artists'] = FeaturedArtist.objects.filter(is_published=True).order_by('-date_featured')
        return context


class FeaturedArtistView(UserPaneMixin, TemplateView):
    template_name = 'fanart/chamber_of_stars/featured_artist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        month_featured = kwargs.get('month_featured', None)
        year, month = month_featured.split('-')
        context['featured_artist'] = get_object_or_404(FeaturedArtist, date_featured__month=month, date_featured__year=year, is_published=True)

        return context

class FeaturedPicturesView(TemplateView):
    template_name = 'fanart/chamber_of_stars/featured_pictures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_pictures'] = FeaturedPicture.objects.filter(is_published=True).all()
        return context
