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


class CommentsView(ArtManagerPaneView):
    template_name = 'artmanager/comments.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'comments'
        return super(CommentsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CommentsView, self).get_context_data(**kwargs)

        comment_type = kwargs.get('comment_type')
        if comment_type == None:
            if self.request.user.is_artist:
                comment_type = 'received'
            else:
                comment_type = 'sent'

        if comment_type == 'received':
            comments = models.PictureComment.objects.filter(picture__artist=self.request.user).order_by('-date_posted')
            show_all = False
            if self.request.GET.get('show_all') == '1':
                show_all = True
            if not show_all:
                comments = comments.filter(is_received=False)
            context['show_all'] = show_all
        elif comment_type == 'sent':
            comments = self.request.user.picturecomment_set.all().order_by('-date_posted')

        context['comments_paginator'] = Paginator(comments, settings.COMMENTS_PER_PAGE_ARTMANAGER)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            comments_page = context['comments_paginator'].page(page)
        except EmptyPage:
            comments_page = context['comments_paginator'].page(1)

        context['comments'] = comments_page
        context['comment_type'] = comment_type
        context['pages_link'] = utils.PagesLink(len(comments), settings.COMMENTS_PER_PAGE_ARTMANAGER, comments_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        return context


class MarkCommentsReadView(APIView):

    def post(self, request):
        response = {'success': False}
        for comment_id in (request.POST.get('comment_ids')).split(','):
            if not comment_id:
                continue
            try:
                comment = models.PictureComment.objects.get(pk=comment_id, picture__artist=request.user)
                comment.is_received = True
                comment.save()
                logger.info(comment.id)
            except models.PictureComment.DoesNotExist:
                pass
        response['success'] = True
        return Response(response)


class CommentDetailView(LoginRequiredMixin, DetailView):
    template_name = 'artmanager/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.PictureComment, (Q(picture__artist=self.request.user) | Q(user=self.request.user)), pk=self.kwargs['comment_id'])

    def get_context_data(self, **kwargs):
        context = super(CommentDetailView, self).get_context_data(**kwargs)
        context['comment'] = self.object
        return context


class CommentDeleteView(LoginRequiredMixin, UpdateView):
    model = models.PictureComment
    form_class = forms.DeleteCommentForm
    template_name = 'artmanager/comment.html'

    def get_object(self):
        return get_object_or_404(models.PictureComment, (Q(picture__artist=self.request.user) | Q(user=self.request.user)), pk=self.kwargs['comment_id'])

    def form_valid(self, form):
        self.object.is_deleted = True
        response = super(CommentDeleteView, self).form_valid(form)

        logger.info(self.request.POST)

        return response

    def get_success_url(self):
        return reverse('artmanager:comment-detail', kwargs={'comment_id': self.object.id})


