from django.conf import settings
from django.views.generic import TemplateView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from fanart.views import UserPaneMixin
from fanart.models import Showcase, Contest
from fanart.utils import PagesLink


class ShowcasesView(UserPaneMixin, TemplateView):
    template_name = 'fanart/showcases/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        showcase_id = kwargs.get('showcase_id', None)

        if showcase_id:
            context['showcase'] = get_object_or_404(Showcase, pk=showcase_id)

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

        else:
            context['contest'] = Contest.objects.filter(type='global', date_start__lt=timezone.now(), is_active=True).order_by('-date_created').first()
            context['contest_entries'] = context['contest'].winning_entries

            context['showcases'] = Showcase.objects.filter(is_visible=True).order_by('id')

        return context


class ShowcaseView(UserPaneMixin, TemplateView):
    template_name = 'fanart/showcases/showcase.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        showcase_id = kwargs.get('showcase_id', None)

        if showcase_id:
            context['showcase'] = get_object_or_404(Showcase, pk=showcase_id)

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
