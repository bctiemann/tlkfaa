

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


class ContestsView(ArtManagerPaneView):
    template_name = 'artmanager/contests.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'contests'
        return super(ContestsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContestsView, self).get_context_data(**kwargs)

#        contests = self.request.user.contest_set.filter(type='personal').order_by('-date_created')
        contests = self.request.user.contest_set.all().order_by('-date_created')
        context['unpublished_contests'] = contests.filter(is_active=False, is_cancelled=False)[0:20]
        context['published_contests'] = contests.filter(is_active=True)[0:20]

        return context


class ContestCreateView(LoginRequiredMixin, CreateView):
    model = models.Contest
    form_class = forms.ContestForm

    def form_valid(self, form):
        logger.info(self.request.POST)
        response = {'success': False}

        contest = form.save(commit=False)
        contest.creator = self.request.user
        contest.type = 'personal'
        contest.is_active = False
        contest.save()

        response = {'success': True}
        return JsonResponse(response)


class ContestUpdateView(LoginRequiredMixin, AjaxableResponseMixin, UpdateView):
    model = models.Contest
    form_class = forms.ContestForm

    def get_object(self, queryset=None):
        return get_object_or_404(models.Contest, pk=self.kwargs['contest_id'], creator=self.request.user)


class ContestPublishView(ContestUpdateView):
    form_class = forms.ContestPublishForm

    def form_valid(self, form):
        response = {'success': False}

        contest = form.save(commit=False)
        if contest.is_active:
            contest.date_start = timezone.now()
        contest.save()

        response = {'success': True}
        return JsonResponse(response)


class ContestCancelView(ContestUpdateView):
    form_class = forms.ContestCancelForm


class ContestDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Contest

    def get_object(self):
        return get_object_or_404(models.Contest, pk=self.kwargs['contest_id'], creator=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = {'success': False}

        self.object = self.get_object()
        logger.info(self.object)

        self.object.delete()

        response['success'] = True

        return JsonResponse(response)


class ContestEntriesView(LoginRequiredMixin, DetailView):
    model = models.Contest
    template_name = 'artmanager/contest_entries.html'

    def get_object(self):
        return get_object_or_404(models.Contest, pk=self.kwargs['contest_id'], creator=self.request.user)

