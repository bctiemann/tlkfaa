from django.conf import settings
from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from fanart.views import UserPaneMixin
from fanart.models import Showcase, FeaturedArtist, FeaturedPicture
from fanart.utils import PagesLink


class PaginationMixin:

    def get_pictures(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pictures = self.get_pictures()

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


class ShowcasesView(UserPaneMixin, ListView):
    template_name = 'fanart/chamber_of_stars/showcases.html'
    model = Showcase

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_visible=True).order_by('id')


class ShowcaseView(UserPaneMixin, PaginationMixin, DetailView):
    template_name = 'fanart/chamber_of_stars/showcase.html'
    model = Showcase
    pk_url_kwarg = 'showcase_id'

    def get_pictures(self):
        pictures = self.object.pictures.order_by('date_uploaded')
        return pictures.filter(artist__is_active=True)


class FeaturedArtistsView(UserPaneMixin, ListView):
    template_name = 'fanart/chamber_of_stars/featured_artists.html'
    model = FeaturedArtist
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_obj = context['page_obj']
        context['pages_link'] = PagesLink(
            len(self.object_list),
            self.paginate_by,
            page_obj.number,
            is_descending=True,
            base_url=self.request.path,
            query_dict=self.request.GET,
        )

        return context


class FeaturedArtistView(UserPaneMixin, TemplateView):
    template_name = 'fanart/chamber_of_stars/featured_artist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        month_featured = kwargs.get('month_featured', None)
        year, month = month_featured.split('-')
        context['featured_artist'] = get_object_or_404(FeaturedArtist, date_featured__month=month, date_featured__year=year, is_published=True)

        return context


class FeaturedPicturesView(UserPaneMixin, ListView):
    template_name = 'fanart/chamber_of_stars/featured_pictures.html'
    model = FeaturedPicture
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_obj = context['page_obj']
        context['pages_link'] = PagesLink(
            len(self.object_list),
            self.paginate_by,
            page_obj.number,
            is_descending=True,
            base_url=self.request.path,
            query_dict=self.request.GET,
        )

        return context
