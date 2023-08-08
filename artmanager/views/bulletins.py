

from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
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


class BulletinsView(ArtManagerPaneView):
    template_name = 'artmanager/bulletins.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'bulletins'
        return super(BulletinsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BulletinsView, self).get_context_data(**kwargs)

        bulletins = self.request.user.bulletin_set.all().order_by('-date_posted')
        context['unpublished_bulletins'] = bulletins.filter(is_published=False)[0:20]
        context['published_bulletins'] = bulletins.filter(is_published=True)[0:20]

        return context


class BulletinCreateView(LoginRequiredMixin, CreateView):
    model = models.Bulletin
    form_class = forms.BulletinForm

    def form_valid(self, form):
        logger.info(self.request.POST)
        response = {'success': False}

        bulletin = form.save(commit=False)
        bulletin.user = self.request.user
        if settings.BULLETINS_MODERATED:
            bulletin.is_published = False
        else:
            bulletin.is_published = True
            bulletin.date_published = timezone.now()
        bulletin.save()

        tasks.send_bulletin_posted_email.delay(bulletin.id)

        response = {'success': True}
        return JsonResponse(response)


class BulletinUpdateView(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    model = models.Bulletin
    form_class = forms.BulletinForm

    def get_object(self, queryset=None):
        return get_object_or_404(models.Bulletin, pk=self.kwargs['bulletin_id'], user=self.request.user)


class BulletinDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Bulletin

    def get_object(self):
        return get_object_or_404(models.Bulletin, pk=self.kwargs['bulletin_id'], user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = {'success': False}

        self.object = self.get_object()
        logger.info(self.object)

        self.object.delete()

        response['success'] = True

        return JsonResponse(response)

