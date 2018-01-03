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
from trading_tree import forms
from trading_tree.models import Offer, Claim

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

THREE_MONTHS = 90
ONE_MONTH = 180


class TradingTreeView(fanart_views.UserPaneMixin, TemplateView):
    template_name = 'trading_tree/trading_tree.html'

    def get_context_data(self, **kwargs):
        context = super(TradingTreeView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        offer_type = kwargs.get('offer_type')
        if not offer_type:
            offer_type = 'icon'

        offer_id = self.request.GET.get('offer_id', None)
        if offer_id:
            context['offer'] = get_object_or_404(Offer, pk=offer_id)
            if self.request.user.is_authenticated():
                context['my_claims_for_offer'] = context['offer'].claim_set.filter(user=self.request.user)

        three_months_ago = timezone.now() - timedelta(days=THREE_MONTHS)
        context['offers'] = Offer.objects.filter(is_visible=True, is_active=True, type=offer_type, date_posted__gt=three_months_ago).order_by('-date_posted')

        if self.request.user.is_authenticated() and ((offer_type == 'icon' and self.request.user.icon_claims_ready.exists()) or (offer_type == 'adoptable' and self.request.user.adoptable_claims_ready.exists())):
            context['show_for_you'] = True
            if offer_type == 'icon':
                context['claims_for_you'] = self.request.user.icon_claims_ready.all()
            elif offer_type == 'adoptable':
                context['claims_for_you'] = self.request.user.adoptable_claims_ready.all()

        context['offer_type'] = offer_type
        return context


class PostClaimView(CreateView):
    model = Claim
    form_class = forms.ClaimForm
    template_name = 'trading_tree/offer.html'

    def form_valid(self, form):
        logger.info(self.request.POST)
        response = {'success': False}
        offer = Offer.objects.get(pk=self.request.POST.get('offer', None))

        claim = form.save(commit=False)
        claim.offer = offer
        claim.user = self.request.user
        claim.save()

        return JsonResponse(response)


class UploadClaimView(UpdateView):
    model = Claim
    form_class = forms.UploadClaimForm
    template_name = 'trading_tree/claim.html'

    def get_object(self):
        return get_object_or_404(Claim, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        response = {'success': False}

        self.object.picture = self.request.FILES['picture']
        self.object.filename = self.request.FILES['picture'].name
        self.object.date_uploaded = timezone.now()
        super(UploadClaimView, self).form_valid(form)

        return JsonResponse(response)

    def get_context_data(self, *args, **kwargs):
        context = super(UploadClaimView, self).get_context_data(*args, **kwargs)
        context['claim'] = self.object
        return context


class RemoveClaimUploadView(UpdateView):
    model = Claim
    form_class = forms.UploadClaimForm
    template_name = 'trading_tree/claim.html'

    def get_object(self):
        return get_object_or_404(Claim, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        self.object.filename = ''
        self.object.date_fulfilled = None
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.object.picture.name))
            os.remove(os.path.join(self.object.thumbnail_path))
        except OSError:
            pass
        self.object.picture = None
        return super(RemoveClaimUploadView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(RemoveClaimUploadView, self).get_context_data(*args, **kwargs)
        context['claim'] = self.object
        return context


class AcceptClaimView(UpdateView):
    model = Claim
    form_class = forms.AcceptClaimForm
    template_name = 'trading_tree/for_you.html'

    def get_object(self):
        return get_object_or_404(Claim, pk=self.kwargs['claim_id'], user=self.request.user)

    def form_valid(self, form):
        if self.object.offer.type == 'icon':
            self.object.date_fulfilled = timezone.now()
        elif self.object.offer.type == 'adoptable':

            comment_append = ''
            if self.object.offer.character.profile_picture:
                comment_append = '\n\nPrevious owner\'s reference picture: http://{0}/picture/{1}'.format(settings.SERVER_HOST, self.object.offer.character.profile_picture.id)
            elif self.object.offer.character.profile_coloring_picture:
                comment_append = '\n\nPrevious owner\'s reference picture: http://{0}/ColoringCave/{1}'.format(settings.SERVER_HOST, self.object.offer.character.profile_coloring_picture.id)

            self.object.offer.character.owner = self.request.user
            self.object.offer.character.profile_picture = None
            self.object.offer.character.profile_coloring_picture = None
            self.object.offer.character.date_adopted = timezone.now()
            self.object.offer.character.adopted_from = self.object.offer.artist
            self.object.offer.character.description += comment_append
            self.object.offer.character.save()

            self.object.offer.is_active = False
            self.object.offer.is_visible = False
            self.object.offer.adopted_by = self.request.user
            self.object.offer.save()

            self.object.offer.artist.refresh_num_characters()
            self.request.user.refresh_num_characters()

#                                Accepting this adoptable into your Characters section...

        return super(AcceptClaimView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(AcceptClaimView, self).get_context_data(*args, **kwargs)
        context['claim'] = self.object
        return context

    def get_success_url(self):
        return reverse('accept-claim', kwargs={'claim_id': self.object.id})


class ChooseAdopterView(UpdateView):
    model = Claim
    form_class = forms.AcceptClaimForm

    def get_object(self):
        return get_object_or_404(Claim, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        logger.info(self.object.date_fulfilled)
        if self.object.date_fulfilled:
            self.object.date_fulfilled = None
        else:
            self.object.date_fulfilled = timezone.now()
        return super(ChooseAdopterView, self).form_valid(form)


class RemoveClaimView(DeleteView):
    model = Claim

    def get_object(self):
        return get_object_or_404(Claim, (Q(user=self.request.user) | Q(offer__artist=self.request.user)), pk=self.kwargs['claim_id'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(self.object.picture.name)
        return super(RemoveClaimView, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('offer', kwargs={'offer_id': self.object.offer.id})


class OfferView(DetailView):
    models = Offer
    template_name = 'trading_tree/offer_detail.html'

    def get_object(self):
        return get_object_or_404(Offer, pk=self.kwargs['offer_id'])


class EditOfferView(UpdateView):
    models = Offer
    form_class = forms.OfferForm
    template_name = 'trading_tree/edit_offer.html'

    def get_object(self):
        return get_object_or_404(Offer, pk=self.kwargs['offer_id'], artist=self.request.user)


class RemoveOfferView(UpdateView):
    models = Offer
    form_class = forms.RemoveOfferForm
    template_name = 'trading_tree/edit_offer.html'

    def get_object(self):
        return get_object_or_404(Offer, pk=self.kwargs['offer_id'], artist=self.request.user)

    def form_valid(self, form):
        response = {'success': False}

        self.object.is_active = False
        self.object.is_visible = False
        self.object.save()

        response['success'] = True

        return JsonResponse(response)


class OfferStatusView(APIView):

    def get(self, request, offer_id=None):
        response = {}
        offer = get_object_or_404(Offer, pk=offer_id)
        for claim in offer.claim_set.all():
            if claim.picture:
                response[claim.id] = {
                    'thumbnail_url': claim.thumbnail_url,
                    'thumbnail_done': claim.thumbnail_created,
                }
        return Response(response)


