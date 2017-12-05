from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count
from django.db import connection
from django.forms import ValidationError

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models
from fanart import views as fanart_views
from coloring_cave import forms
from coloring_cave.models import Base, ColoringPicture

from fanart.response import JSONResponse, response_mimetype
from fanart.serialize import serialize

from datetime import timedelta
import uuid
import json
import random
import mimetypes
import os

import logging
logger = logging.getLogger(__name__)


class ColoringCaveView(fanart_views.UserPaneMixin, TemplateView):
    template_name = 'fanart/coloringcave.html'

    def get_context_data(self, **kwargs):
        context = super(ColoringCaveView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        sort_by = self.request.GET.get('sort_by', None)
        if not sort_by in ['popularity', 'date']:
            sort_by = 'popularity'

        coloring_base_id = kwargs.get('coloring_base_id', None)
        if coloring_base_id:
            context['coloring_base'] = get_object_or_404(Base, pk=coloring_base_id)
        else:
            coloring_bases = Base.objects.filter(is_visible=True)
            if sort_by == 'popularity':
                coloring_bases = coloring_bases.order_by('-num_colored')
            elif sort_by == 'date':
                coloring_bases = coloring_bases.order_by('-date_posted')

            context['coloring_bases'] = coloring_bases[0:100]
        context['sort_by'] = sort_by

        return context


class ColoringCavePictureView(fanart_views.UserPaneMixin, TemplateView):
    template_name = 'fanart/coloringcave.html'

    def get_context_data(self, **kwargs):
        context = super(ColoringCavePictureView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        context['coloring_bases'] = coloring_bases[0:100]
        context['sort_by'] = sort_by

        return context

class ColoringPicturesView(DetailView):
    model = Base
    template_name = 'includes/colored_pictures.html'

    def get_object(self):
        return get_object_or_404(Base, pk=self.kwargs['coloring_base_id'])

    def get_context_data(self, *args, **kwargs):
        context = super(ColoringPicturesView, self).get_context_data(*args, **kwargs)
        context['coloring_base'] = self.object
        return context


class UploadColoringPictureView(CreateView):
    model = ColoringPicture
    form_class = forms.UploadColoringPictureForm
    template_name = 'includes/colored_pictures.html'

#    def get_object(self):
#        return get_object_or_404(models.ColoringPic, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        response = {'success': False}

        coloring_base = get_object_or_404(Base, pk=self.kwargs['coloring_base_id'])

        coloring_picture = form.save(commit=False)
        coloring_picture.artist = self.request.user
        coloring_picture.base = coloring_base
        coloring_picture.save()

        coloring_picture.picture = self.request.FILES['picture']
        coloring_picture.filename = self.request.FILES['picture'].name
        coloring_picture.save()

        coloring_base.refresh_num_colored()

#        self.object.filename = self.request.FILES['picture'].name
#        self.object.date_uploaded = timezone.now()
        super(UploadColoringPictureView, self).form_valid(form)

        return JsonResponse(response)


    def get_context_data(self, *args, **kwargs):
        context = super(UploadColoringPictureView, self).get_context_data(*args, **kwargs)
        context['coloring_base'] = self.object
        return context


class ColoringPictureStatusView(APIView):

    def get(self, request, coloring_base_id=None):
        response = {}
        offer = get_object_or_404(Base, pk=coloring_base_id)
        for coloring_picture in offer.coloringpicture_set.all():
            if coloring_picture.picture and coloring_picture.filename:
                response[coloring_picture.id] = {
                    'thumbnail_url': coloring_picture.thumbnail_url,
                    'thumbnail_done': coloring_picture.thumbnail_created,
                }
        return Response(response)


class RemoveColoringPictureView(DeleteView):
    model = ColoringPicture

    def get_object(self):
        return get_object_or_404(ColoringPicture, (Q(artist=self.request.user) | Q(base__creator=self.request.user)), pk=self.kwargs['coloring_picture_id'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(self.object.picture.name)
        result = super(RemoveColoringPictureView, self).delete(self, request, *args, **kwargs)
        self.object.base.refresh_num_colored()
        return result

    def get_success_url(self):
        return reverse('coloring-pictures', kwargs={'coloring_base_id': self.object.base.id})

