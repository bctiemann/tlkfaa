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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models, utils, tasks
from fanart import views as fanart_views
from pms import forms
from pms.models import PrivateMessage

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


class PMsView(LoginRequiredMixin, TemplateView):
    template_name = 'includes/private_messages.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PMsView, self).get_context_data(*args, **kwargs)

        box = kwargs.get('box', 'in')
        pms = None
        if box == 'in':
             pms = self.request.user.pms_received.filter(deleted_by_recipient=False)
        elif box == 'out':
             pms = self.request.user.pms_sent.filter(deleted_by_sender=False)
        elif box == 'trash':
             pms = self.request.user.pms_sent.filter(deleted_by_sender=True).union(self.request.user.pms_received.filter(deleted_by_recipient=True))

        pms = pms.order_by('-date_sent')

        context['pms_paginator'] = Paginator(pms, settings.PMS_PER_PAGE)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            pms_page = context['pms_paginator'].page(page)
        except EmptyPage:
            pms_page = context['pms_paginator'].page(1)

        context['box'] = box
        context['pms'] = pms_page
        if self.request.GET.get('showstatus'):
            context['showstatus'] = True
        if self.request.GET.get('showpages'):
            context['showpages'] = True

        context['pages_link'] = utils.PagesLink(len(pms), settings.PMS_PER_PAGE, pms_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET, selection_type='ajax')

        return context


class PMView(LoginRequiredMixin, DetailView):
    model = PrivateMessage
    template_name = 'includes/pm.html'

    def get_object(self):
        return get_object_or_404(PrivateMessage, (Q(sender=self.request.user) | Q(recipient=self.request.user)), pk=self.kwargs['pm_id'])

    def get_context_data(self, *args, **kwargs):
        context = super(PMView, self).get_context_data(*args, **kwargs)

        if self.object.recipient == self.request.user and self.object.date_viewed == None:
            self.object.date_viewed = timezone.now()
            self.object.save()

        context['pm'] = self.object
        context['blocked'] = models.Block.objects.filter(user=context['pm'].sender, blocked_user=self.request.user).exists()

        return context


class PMCreateView(LoginRequiredMixin, CreateView):
    model = PrivateMessage
    form_class = forms.PMForm

    def get(self, *args, **kwargs):
        return redirect('artmanager:private-msgs')

    def form_invalid(self, form):
        raise Http404

    def form_valid(self, form):
        pm = form.save(commit=False)
        pm.sender = self.request.user
        if pm.sender == pm.recipient:
            raise Http404
        pm.save()
        pm.root_pm = pm
        if pm.reply_to:
            pm.reply_to.date_replied = timezone.now()
            pm.reply_to.save()
            pm.subject = pm.reply_to.subject
            if not pm.subject.startswith('Re: '):
                pm.subject = 'Re: {0}'.format(pm.subject)
            pm.root_pm = pm.reply_to.root_pm
        pm.save()

        recipient = form.cleaned_data['recipient']
        print(recipient)
        if recipient.email_pms:
            email_context = {'pm': pm, 'sender': self.request.user, 'base_url': settings.SERVER_BASE_URL}
            subject = 'TLKFAA Private Message from {0}'.format(self.request.user.username)
            tasks.send_email.delay(
                recipients=[recipient.email],
                subject=subject,
                context=email_context,
                text_template='email/pm_sent.txt',
                html_template='email/pm_sent.html',
                bcc=[settings.DEBUG_EMAIL]
            )

        response = super(PMCreateView, self).form_valid(form)
        return response

    def get_success_url(self):
        return reverse('artmanager:private-msgs', kwargs={'box': 'out'})


class PMSuccessView(PMView):
    template_name = 'includes/pm_success.html'


class PMShoutView(LoginRequiredMixin, TemplateView):
    template_name = 'includes/pm.html'

    def get_context_data(self, **kwargs):
        context = super(PMShoutView, self).get_context_data(**kwargs)

        context['shout'] = get_object_or_404(models.Shout, pk=self.kwargs['shout_id'], artist=self.request.user)
        context['recipient'] = context['shout'].user
        context['blocked'] = models.Block.objects.filter(user=context['recipient'], blocked_user=self.request.user).exists()

        return context


class PMUserView(LoginRequiredMixin, TemplateView):
    template_name = 'includes/pm.html'

    def get_context_data(self, **kwargs):
        context = super(PMUserView, self).get_context_data(**kwargs)

        if 'recipient_id' in self.kwargs and self.kwargs['recipient_id']:
            context['recipient'] = get_object_or_404(models.User, pk=self.kwargs['recipient_id'])
            context['blocked'] = models.Block.objects.filter(user=context['recipient'], blocked_user=self.request.user).exists()

            shout_id = self.request.GET.get('shout_id', None)
            bulletin_id = self.request.GET.get('bulletin_id', None)
            if shout_id:
                context['shout'] = get_object_or_404(models.Shout, pk=shout_id, artist=self.request.user)
            if bulletin_id:
                context['bulletin'] = get_object_or_404(models.Bulletin, pk=bulletin_id, user=context['recipient'])

        return context


class PMsMoveView(LoginRequiredMixin, APIView):

    def post(self, request, action):
        response = {'success': False, 'action': action, 'pm_ids': request.POST.get('pm_ids')}
        logger.info(action)
        for pm_id in (request.POST.get('pm_ids')).split(','):
            if not pm_id:
                continue
            try:
                pm = PrivateMessage.objects.get((Q(sender=self.request.user) | Q(recipient=self.request.user)), pk=pm_id)
                logger.info(pm)
                if action == 'delete':
                    if pm.sender == request.user:
                        logger.info('deleting sender')
                        pm.deleted_by_sender = True
                    elif pm.recipient == request.user:
                        logger.info('deleting recipient')
                        pm.deleted_by_recipient = True
                elif action == 'restore':
                    if pm.sender == request.user:
                        pm.deleted_by_sender = False
                    elif pm.recipient == request.user:
                        pm.deleted_by_recipient = False
                pm.save()
            except PrivateMessage.DoesNotExist:
                logger.info('{0} not found'.format(pm_id))
                continue
        response['success'] = True
        return Response(response)

