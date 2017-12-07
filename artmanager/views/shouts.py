from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render, render_to_response, redirect, reverse, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView, FormMixin
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count

from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models, utils, tasks
from fanart.views import UserPaneMixin
from fanart.forms import AjaxableResponseMixin
from artmanager import forms
from trading_tree.models import Offer, Claim
from coloring_cave.models import Base, ColoringPicture
from . import ArtManagerPaneView

import json
import hashlib
import os
import shutil
from PIL import Image

import logging
logger = logging.getLogger(__name__)


class ShoutsView(ArtManagerPaneView):
    template_name = 'artmanager/shouts.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'shouts'
        return super(ShoutsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShoutsView, self).get_context_data(**kwargs)

        shout_type = kwargs.get('shout_type')
        if shout_type == None:
            if self.request.user.is_artist:
                shout_type = 'received'
            else:
                shout_type = 'sent'

        if shout_type == 'received':
            shouts = self.request.user.shouts_received.all().order_by('-date_posted')
            show_all = False
            if self.request.GET.get('show_all') == '1':
                show_all = True
            if not show_all:
                shouts = shouts.filter(is_received=False)
            context['show_all'] = show_all
        elif shout_type == 'sent':
            shouts = self.request.user.shout_set.all().order_by('-date_posted')

        context['shouts_paginator'] = Paginator(shouts, settings.SHOUTS_PER_PAGE_ARTMANAGER)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            shouts_page = context['shouts_paginator'].page(page)
        except EmptyPage:
            shouts_page = context['shouts_paginator'].page(1)

        context['shouts'] = shouts_page
        context['shout_type'] = shout_type
        context['pages_link'] = utils.PagesLink(len(shouts), settings.SHOUTS_PER_PAGE_ARTMANAGER, shouts_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        return context


class MarkShoutsReadView(APIView):

    def post(self, request):
        response = {'success': False}
        for shout_id in (request.POST.get('comment_ids')).split(','):
            if not shout_id:
                continue
            try:
                shout = models.Shout.objects.get(pk=shout_id, artist=request.user)
                shout.is_received = True
                shout.save()
                logger.info(shout.id)
            except models.Shout.DoesNotExist:
                pass
        response['success'] = True
        return Response(response)


class ShoutDetailView(LoginRequiredMixin, DetailView):
    template_name = 'artmanager/shout.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Shout, (Q(artist=self.request.user) | Q(user=self.request.user)), pk=self.kwargs['shout_id'])


class ShoutDeleteView(LoginRequiredMixin, UpdateView):
    model = models.Shout
    form_class = forms.DeleteShoutForm
    template_name = 'artmanager/shout.html'

    def get_object(self):
        return get_object_or_404(models.Shout, (Q(artist=self.request.user) | Q(user=self.request.user)), pk=self.kwargs['shout_id'])

    def form_valid(self, form):
        self.object.is_deleted = True
        response = super(ShoutDeleteView, self).form_valid(form)

        logger.info(self.request.POST)

        return response

    def get_success_url(self):
        return reverse('artmanager:shout-detail', kwargs={'shout_id': self.object.id})


