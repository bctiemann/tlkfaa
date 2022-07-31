import hashlib

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden, HttpResponseNotAllowed
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView, FormMixin
from django.utils import timezone
from django.contrib.auth import (
    login, authenticate, get_user_model, password_validation,
)
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count
from django.db import connection
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models, forms, utils, tasks, serializers
from fanart.forms import AjaxableResponseMixin
from coloring_cave.models import Base, ColoringPicture
from trading_tree.models import Offer, Claim
from sketcher.models import ActiveUser, Drawpile

from fanart.response import JSONResponse, response_mimetype
from fanart.serialize import serialize

from datetime import timedelta
from itertools import chain
import uuid
import json
import random
import mimetypes
import os
import requests

from ratelimit.mixins import RatelimitMixin

import logging
logger = logging.getLogger(__name__)

THREE_MONTHS = 90
ONE_MONTH = 30


# def favicon(request):
#     return redirect(static('images/favicon-96x96.png'))
#
# def robots(request):
#     return redirect(static('robots.txt'))


# class ErrorHandler500(TemplateView):
#     template_name = '500.html'
#
# class ErrorHandler404(TemplateView):
#     template_name = '404.html'
#
# class ErrorHandler403(TemplateView):
#     template_name = '403.html'


class LoginView(LoginView):
    form_class = forms.LoginForm

    def get(self, request, *args, **kwargs):
        return redirect('home')

    def form_valid(self, form):
        self.request.session['django_timezone'] = form.get_user().timezone
        return super(LoginView, self).form_valid(form)

    def form_invalid(self, form):
        self.request.session['login_failed'] = True
        return redirect('home')


class UserPaneMixin(RatelimitMixin):
    ratelimit_key = 'ip'
    ratelimit_rate = '10/m'
    ratelimit_method = 'GET'

    def dispatch(self, request, *args, **kwargs):
        r = super().dispatch(request, *args, **kwargs)
        self.ratelimit_block = not request.user.is_authenticated
        return r

    def get_community_art_data(self):
        community_art_data = {}
        icons_publish_start_date = timezone.now() - timedelta(weeks=3)
        adoptables_publish_start_date = timezone.now() - timedelta(days=30*6)
        adoptables_mine_start_date = timezone.now() - timedelta(days=30)
        community_art_data['icons'] = Offer.objects.filter(
            type='icon',
            is_active=True,
            is_visible=True,
            date_posted__gt=icons_publish_start_date,
        )
        community_art_data['icons_today'] = Offer.objects.filter(
            type='icon',
            is_active=True,
            is_visible=True,
            date_posted__date__gte=timezone.now(),
        )
        community_art_data['icons_mine'] = Claim.objects.filter(
            offer__type='icon',
            offer__is_active=True,
            offer__is_visible=True,
            date_fulfilled__isnull=True,
            filename='',
            offer__date_posted__gt=icons_publish_start_date,
            user=self.request.user,
        )
        community_art_data['adoptables'] = Offer.objects.filter(
            type='adoptable',
            is_active=True,
            is_visible=True,
            date_posted__gt=adoptables_publish_start_date,
        )
        community_art_data['adoptables_unclaimed'] = community_art_data['adoptables'].filter(adopted_by__isnull=True)
        community_art_data['adoptables_mine'] = Claim.objects.filter(
            offer__type='adoptable',
            offer__is_active=True,
            offer__is_visible=True,
            date_fulfilled__isnull=False,
            offer__date_posted__gt=adoptables_mine_start_date,
            user=self.request.user,
        )
        community_art_data['coloring_bases'] = Base.objects.filter(is_active=True, is_visible=True)
        return community_art_data

    def get_contests_data(self):
        contests_data = {}
        contests_data['contests_new'] = models.Contest.objects.filter(
            type='personal',
            is_active=True,
            is_cancelled=False,
            date_end__gt=timezone.now(),
        ).order_by('-date_start')[0:5]
        contests_data['contests_ending'] = models.Contest.objects.filter(
            type='personal',
            is_active=True,
            is_cancelled=False,
            date_end__gt=timezone.now(),
        ).order_by('-date_end')[0:5]
        return contests_data

    def get_sketcher_users(self):
        return ActiveUser.objects.all()

    def get_drawpile(self):
        return Drawpile.objects.first()

    def get_sketcher_slots(self):
        slots = []
        sketcher_users = self.get_sketcher_users()
        for slot in range(12):
            try:
                slots.append(sketcher_users[slot])
            except IndexError:
                slots.append(None)
        return slots

    def get_context_data(self, **kwargs):
        context = super(UserPaneMixin, self).get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        context['favorite_artists'] = self.request.user.favorite_artists

        context['THUMB_SIZE'] = settings.THUMB_SIZE
        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()

        context['drawpile'] = self.get_drawpile()
        context['sketcher_slots'] = self.get_sketcher_slots()

        self.request.user.update_last_active()

        return context


# Main tab pages

class HomeView(UserPaneMixin, TemplateView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['current_contest'] = models.Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()
        context['admin_announcements'] = models.Bulletin.objects.filter(is_published=True, is_admin=True).order_by('-date_posted')[0:3]
        context['bulletins'] = models.Bulletin.objects.filter(is_published=True, is_admin=False).order_by('-date_posted')[0:5]
        context['recently_active_artists'] = models.User.objects.recently_active(self.request)
        context['last_revision_log'] = models.RevisionLog.objects.order_by('-date_created').first()

        context['upcoming_birthdays'] = models.User.objects.upcoming_birthdays()
        context['aotm'] = models.FeaturedArtist.objects.filter(is_published=True).first()
        context['featured_picture'] = models.FeaturedPicture.objects.filter(is_published=True).first()

        context['login_failed'] = self.request.session.get('login_failed')
        self.request.session['login_failed'] = False

        return context


class RandomPopularView(TemplateView):
    template_name = 'includes/random_popular.html'

    def get_context_data(self, **kwargs):
        context = super(RandomPopularView, self).get_context_data(**kwargs)
        context['random_popular'] = models.Picture.objects.random_popular[0:12]
        context['featured_picture'] = models.FeaturedPicture.objects.filter(is_published=True).first()
        return context


class ArtistsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artists.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistsView, self).get_context_data(**kwargs)

        context['show_search_input'] = False

        list_type = kwargs.get('list', self.request.GET.get('list', settings.DEFAULT_ARTISTS_VIEW))
        if not list_type in models.artists_tabs:
            list_type = settings.DEFAULT_ARTISTS_VIEW

        start = int(self.request.GET.get('start', 0))
        initial = self.request.GET.get('initial', None)

        artists = models.User.objects.filter(is_active=True, is_artist=True, num_pictures__gt=0)
        one_month_ago = timezone.now() - timedelta(days=180)
        if list_type == 'name':
            if not initial:
                raise Http404

            artists = artists.filter(username__istartswith=initial).order_by('username')
            context['artists_paginator'] = Paginator(artists, settings.ARTISTS_PER_PAGE_INITIAL)
            try:
                page = int(self.request.GET.get('page', 1))
            except ValueError:
                page = 1
            try:
                artists_page = context['artists_paginator'].page(page)
            except EmptyPage:
                artists_page = context['artists_paginator'].page(1)
        elif list_type == 'newest':
            artists = artists.order_by('-date_joined')
        elif list_type == 'recentactive':
            artists = artists.order_by('-last_upload')
        elif list_type == 'toprated':
            artists = artists.extra(select={'rating': 'num_favepics / num_pictures * num_faves'}).order_by('-rating')
        elif list_type == 'topratedactive':
            artists = artists.filter(last_upload__gt=one_month_ago).extra(select={'rating': 'num_favepics / num_pictures * num_faves'}).order_by('-rating')
        elif list_type == 'prolific':
            artists = artists.order_by('-num_pictures')
        elif list_type == 'random':
            artists = artists.order_by('?')
        elif list_type == 'search':
            term = self.request.GET.get('term', None)
            if not term:
                context['show_search_input'] = True
            if term:
                context['term'] = term
                artists = artists.filter(username__icontains=term).order_by('sort_name')
            else:
                artists = artists.filter(id__isnull=True)

        context['list_type'] = list_type
        context['per_page'] = settings.ARTISTS_PER_PAGE
        context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['initial'] = initial
        context['artists'] = artists[start:start + context['count']]
        if list_type == 'name':
            context['artists'] = artists_page
            context['count'] = None
            context['pages_link'] = utils.PagesLink(len(artists), settings.ARTISTS_PER_PAGE_INITIAL, artists_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        return context


class ArtworkView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artwork.html'

    def get_context_data(self, **kwargs):
        context = super(ArtworkView, self).get_context_data(**kwargs)

        context['show_search_input'] = False

        default_artwork_view = settings.DEFAULT_ARTWORK_VIEW
        if self.request.user.is_authenticated and self.request.user.unviewedpicture_set.exists():
            default_artwork_view = 'unviewed'

#        mode = kwargs.get('mode', None)
#        if not mode in ['canon', 'fan', 'mosttagged', 'recentlytagged', 'charactername'] and not dir_name:
#            mode = 'canon'

        list_type = kwargs.get('list', self.request.GET.get('list', default_artwork_view))
        if not list_type in models.artwork_tabs:
            list_type = default_artwork_view

        try:
            start = int(self.request.GET.get('start', 0))
        except ValueError:
            start = 0
        try:
            initial = self.request.GET.get('initial', None)
        except ValueError:
            initial = None

        artwork = models.Picture.objects.filter(artist__is_active=True, artist__is_artist=True, artist__num_pictures__gt=0)
        three_months_ago = timezone.now() - timedelta(days=THREE_MONTHS)
        one_month_ago = timezone.now() - timedelta(days=ONE_MONTH)
        if list_type == 'unviewed' and self.request.user.is_authenticated:
            artwork = [uvp.picture for uvp in models.UnviewedPicture.objects.filter(user=self.request.user).order_by('-picture__date_uploaded')]
        elif list_type == 'newest':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago).order_by('-date_uploaded')
        elif list_type == 'newestfaves' and self.request.user.is_authenticated:
            artwork = artwork.filter(date_uploaded__gt=three_months_ago, artist__in=Subquery(self.request.user.favorite_set.filter(picture__isnull=True).values('artist_id'))).order_by('-date_uploaded')
        elif list_type == 'toprated':
            artwork = artwork.filter(num_faves__gt=100).order_by('-num_faves')
        elif list_type == 'topratedrecent':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago).order_by('-num_faves')
        elif list_type == 'random':
            random_ids = random.sample(list(range(models.Picture.objects.all().aggregate(Min('id'))['id__min'], models.Picture.objects.all().aggregate(Max('id'))['id__max'])), 100)
            artwork = artwork.filter(pk__in=random_ids)
        elif list_type in ['search', 'tag', 'character']:
            term = self.request.GET.get('term', None)
            year_from = self.request.GET.get('year_from')
            year_to = self.request.GET.get('year_to')
            current_year = timezone.now().year
            if year_from and year_from.isnumeric() and current_year >= int(year_from) > 0:
                artwork = artwork.filter(date_uploaded__year__gte=year_from)
                context['year_from'] = year_from
            if year_to and year_to.isnumeric() and current_year >= int(year_to) > 0:
                artwork = artwork.filter(date_uploaded__year__lte=year_to)
                context['year_to'] = year_to
            if not term:
                context['show_search_input'] = True
                context['top_300_tags'] = sorted(models.Tag.objects.annotate(num_pictures=Count('picture')).order_by('-num_pictures')[:300], key=lambda tag: tag.num_pictures, reverse=True)
            if term:
                if start == 0:
                    context['show_search_input'] = True
                context['term'] = term
                if list_type == 'search':
                    artwork = artwork.filter(title__icontains=term).order_by('-num_faves')
                    logger.info('Artwork title search by {0} {1}: {2} ({3})'.format(self.request.user, self.request.META['REMOTE_ADDR'], term, start))
                elif list_type == 'tag':
                    logger.info('Artwork tag search by {0} {1}: {2} ({3})'.format(self.request.user, self.request.META['REMOTE_ADDR'], term, start))
                    tag = models.Tag.objects.filter(tag=term).first()
                    if tag:
                        artwork = tag.picture_set.filter(artist__is_active=True, artist__is_artist=True, artist__num_pictures__gt=0).order_by('-num_faves')
                    else:
                        artwork = artwork.filter(id__isnull=True)
                elif list_type == 'character':
                    character_pictures = models.Picture.objects.all()
                    for character_id in term.split(','):
                        try:
                            character_pictures = character_pictures.filter(picturecharacter__character_id=character_id)
                        except ValueError:
                            character_pictures = character_pictures.none()
                        artwork = character_pictures.order_by('-picturecharacter__date_tagged')
            else:
                artwork = artwork.filter(id__isnull=True)

        context['list_type'] = list_type
        context['per_page'] = settings.ARTWORK_PER_PAGE
        try:
            context['count'] = int(self.request.GET.get('count', settings.ARTWORK_PER_PAGE))
        except ValueError:
            context['count'] = settings.ARTWORK_PER_PAGE
        context['next_start'] = start + settings.ARTWORK_PER_PAGE
        context['initial'] = initial
        context['artwork'] = artwork[start:start + context['count']]

        return context


class CharactersView(UserPaneMixin, TemplateView):
    template_name = 'fanart/characters.html'

    def get_context_data(self, **kwargs):
        context = super(CharactersView, self).get_context_data(**kwargs)

        default_characters_view = settings.DEFAULT_CHARACTERS_VIEW

        dir_name = kwargs.get('dir_name', self.request.GET.get('dir_name', None))
        term = self.request.GET.get('term', None)
        if dir_name:
            context['artist'] = get_object_or_404(models.User, is_artist=True, dir_name=dir_name)
            list_type = 'artist'
        else:
            list_type = kwargs.get('list', self.request.GET.get('list', default_characters_view))
            if not list_type in models.characters_tabs and not dir_name:
                list_type = default_characters_view
            if list_type == 'artist':
                if not term or not term.isnumeric():
                    raise Http404
                context['artist'] = get_object_or_404(models.User, is_artist=True, pk=term)

        mode = list_type
        tab_selected = list_type

        try:
            start = int(self.request.GET.get('start', 0))
        except ValueError:
            start = 0
        initial = self.request.GET.get('initial', None)

        characters = models.Character.objects.all()
        if list_type == 'artist':
            characters = characters.filter(owner=context['artist']).order_by('name')
            tab_selected = 'search'
        elif list_type == 'canon':
            characters = characters.filter(is_canon=True).order_by('-num_pictures')
        elif list_type == 'newest':
            characters = characters.order_by('-date_created')
        elif list_type == 'mosttagged':
            characters = characters.filter(num_pictures__gt=0).order_by('-num_pictures')
        elif list_type == 'recentlytagged':
            characters = characters.filter(num_pictures__gt=0).order_by('-date_tagged')
        elif list_type == 'search':
            context['show_search_box'] = True
            match_type = self.request.GET.get('match', 'contains')
            if term:
#                if match_type == 'exact':
#                    characters = characters.filter(species=term)
#                else:
#                    characters = characters.filter(species__icontains=term)
                list_type = self.request.GET.get('list', None)
                logger.info('Character search ({0}): {1}'.format(list_type, term))
                if not list_type in ['artist', 'species', 'charactername']:
                    list_type = 'charactername'
                characters = characters.filter(owner__is_active=True).order_by('name')
                if list_type == 'artist':
                    try:
                        characters = characters.filter(owner__id=term)
                        context['artist'] = get_object_or_404(models.User, is_artist=True, pk=term)
                    except ValueError:
                        pass
                elif list_type == 'species':
                    if match_type == 'exact':
                        characters = characters.filter(species=term)
                    else:
                        characters = characters.filter(species__icontains=term)
                elif list_type == 'charactername':
                    if match_type == 'exact':
                        characters = characters.filter(name=term)
                    else:
                        characters = characters.filter(name__icontains=term)
                if start > 0:
                    context['show_search_box'] = False
                context['term'] = term
            else:
                characters = characters.filter(id__isnull=True)

#        context['characters_paginator'] = Paginator(characters, settings.CHARACTERS_PER_PAGE)
#        try:
#            page = int(self.request.GET.get('page', 1))
#        except ValueError:
#            page = 1
#        try:
#            characters_page = context['characters_paginator'].page(page)
#        except EmptyPage:
#            characters_page = context['characters_paginator'].page(1)


        context['start'] = start

        context['list_type'] = list_type
        context['tab_selected'] = tab_selected
        context['per_page'] = settings.CHARACTERS_PER_PAGE
#        context['characters'] = characters_page
#        context['pages_link'] = utils.PagesLink(len(characters), settings.CHARACTERS_PER_PAGE, characters_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        context['count'] = int(self.request.GET.get('count', settings.CHARACTERS_PER_PAGE))
        context['next_start'] = start + settings.CHARACTERS_PER_PAGE
        context['initial'] = initial
        context['characters'] = characters[start:start + context['count']]

        return context


class ShowcasesView(UserPaneMixin, TemplateView):
    template_name = 'fanart/showcase.html'

    def get_context_data(self, **kwargs):
        context = super(ShowcasesView, self).get_context_data(**kwargs)

        showcase_id = kwargs.get('showcase_id', None)

        if showcase_id:
            context['showcase'] = get_object_or_404(models.Showcase, pk=showcase_id)

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

            context['pages_link'] = utils.PagesLink(len(pictures), settings.PICTURES_PER_PAGE, context['page_number'], is_descending=True, base_url=self.request.path, query_dict=self.request.GET)

        else:
            context['contest'] = models.Contest.objects.filter(type='global', date_start__lt=timezone.now(), is_active=True).order_by('-date_created').first()
            context['contest_entries'] = context['contest'].winning_entries

            context['showcases'] = models.Showcase.objects.filter(is_visible=True).order_by('id')

        return context


# Secondary pages

class FeaturedArtistsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/featured_artists.html'

    def get_context_data(self, **kwargs):
        context = super(FeaturedArtistsView, self).get_context_data(**kwargs)

        month_featured = kwargs.get('month_featured', None)
        if month_featured:
            year, month = month_featured.split('-')
            context['featured_artist'] = get_object_or_404(models.FeaturedArtist, date_featured__month=month, date_featured__year=year, is_published=True)
        else:
            context['featured_artists'] = models.FeaturedArtist.objects.filter(is_published=True).order_by('-date_featured')

        return context


class FeaturedPicturesView(TemplateView):
    template_name = 'fanart/featured_pictures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_pictures'] = models.FeaturedPicture.objects.filter(is_published=True).all()
        return context


class RevisionLogView(UserPaneMixin, TemplateView):
    template_name = 'fanart/revision_log.html'

    def get_context_data(self, **kwargs):
        context = super(RevisionLogView, self).get_context_data(**kwargs)

        context['entries'] = models.RevisionLog.objects.all().order_by('-date_created')

        return context


# Current-user-targeted pages

class FavoritePicturesView(UserPaneMixin, TemplateView):
    template_name = 'fanart/favorite_pictures.html'

    def get_context_data(self, **kwargs):
        context = super(FavoritePicturesView, self).get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        favorite_pictures = self.request.user.favorite_pictures.order_by('date_added', 'picture__date_uploaded')

        context['favorite_pictures_paginator'] = Paginator(favorite_pictures, settings.PICTURES_PER_PAGE)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        reversed_page = context['favorite_pictures_paginator'].num_pages - page + 1

        try:
            context['favorite_pictures'] = context['favorite_pictures_paginator'].page(reversed_page)
        except EmptyPage:
            context['favorite_pictures'] = context['favorite_pictures_paginator'].page(context['favorite_pictures_paginator'].num_pages)
        context['page_number'] = context['favorite_pictures_paginator'].num_pages - context['favorite_pictures'].number + 1

        context['pages_link'] = utils.PagesLink(len(favorite_pictures), settings.PICTURES_PER_PAGE, context['page_number'], is_descending=True, base_url=self.request.path, query_dict=self.request.GET)

        return context


class ApproveRequestView(LoginRequiredMixin, UserPaneMixin, UpdateView):
    model = models.GiftPicture
    template_name = 'fanart/approve_request.html'
    form_class = forms.GiftPictureForm

    def get_object(self):
        return get_object_or_404(models.GiftPicture, hash=self.kwargs['hash'], recipient=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ApproveRequestView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        logger.info(self.object)
        logger.info(self.request.user)
        logger.info(self.request.POST)
        logger.info(form.cleaned_data)
        response = super(ApproveRequestView, self).form_valid(form)
        if self.request.POST.get('approved'):
            self.object.is_active = True
            self.object.date_accepted = timezone.now()
            self.object.save()

            email_context = {'user': self.request.user, 'giftpicture': self.object, 'base_url': settings.SERVER_BASE_URL}
            tasks.send_email.delay(
                recipients=[self.object.sender.email],
                subject='TLKFAA: Art Trade/Request Accepted by {0}'.format(self.request.user.username),
                context=email_context,
                text_template='email/gift_accepted.txt',
                html_template='email/gift_accepted.html',
                bcc=[settings.DEBUG_EMAIL]
            )

        elif self.request.POST.get('declined'):
            self.object.date_declined = timezone.now()
            self.object.save()

            email_context = {'user': self.request.user, 'giftpicture': self.object, 'base_url': settings.SERVER_BASE_URL}
            tasks.send_email.delay(
                recipients=[self.object.sender.email],
                subject='TLKFAA: Art Trade/Request Rejected by {0}'.format(self.request.user.username),
                context=email_context,
                text_template='email/gift_rejected.txt',
                html_template='email/gift_rejected.html',
                bcc=[settings.DEBUG_EMAIL]
            )

        return response

    def get_success_url(self):
        return reverse('approve-request-success', kwargs={'hash': self.object.hash})


class ApproveRequestSuccessView(LoginRequiredMixin, DetailView):
    model = models.GiftPicture
    template_name = 'fanart/approve_request_success.html'
    form_class = forms.GiftPictureForm

    def get_object(self):
        return get_object_or_404(models.GiftPicture, hash=self.kwargs['hash'], recipient=self.request.user)


# Sidebar boxes

class UserBoxSetView(APIView):

    user_box_names = (
        'favorite_artists_box',
        'favorite_pictures_box',
        'sketcher_box',
        'community_art_box',
        'contests_box',
        'tool_box',
    )

    def post(self, request):
        response = {}
        serializer = serializers.UserBoxSerializer(data=request.POST)
        if not serializer.is_valid():
            response['errors'] = serializer.errors
            return Response(response)
        box = serializer.data['box_name']
        if box in self.user_box_names:
            request.session[box] = serializer.data['is_shown']
        return Response(response)


class FavoriteArtistsBoxView(UserPaneMixin, TemplateView):
    template_name = 'fanart/userpane/favorite_artists.html'


class FavoritePicturesBoxView(UserPaneMixin, TemplateView):
    template_name = 'fanart/userpane/favorite_pictures.html'


class SketcherBoxView(UserPaneMixin, TemplateView):
    template_name = 'fanart/userpane/sketcher.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            self.request.user.update_last_active()
        context = super().get_context_data(**kwargs)
        context['drawpile'] = self.get_drawpile()
        context['sketcher_slots'] = self.get_sketcher_slots()
        return context


class CommunityArtBoxView(UserPaneMixin, TemplateView):
    template_name = 'fanart/userpane/community_art.html'

    def get_context_data(self, **kwargs):
        context = super(CommunityArtBoxView, self).get_context_data(**kwargs)
        context['community_art_data'] = self.get_community_art_data()
        return context


class ContestsBoxView(UserPaneMixin, TemplateView):
    template_name = 'fanart/userpane/contests.html'

    def get_context_data(self, **kwargs):
        context = super(ContestsBoxView, self).get_context_data(**kwargs)
        context['contests_data'] = self.get_contests_data()
        return context


class ToolBoxView(UserPaneMixin, TemplateView):
    template_name = 'fanart/userpane/toolbox.html'


# Registration/recovery

class CheckNameAvailabilityView(APIView):
    permission_classes = ()

    def get(self, request, username=None):
        response = {'is_available': True}
        dir_name = utils.make_dir_name(username)
        response['dir_name'] = dir_name
        try:
            models.validate_unique_username(dir_name)
        except ValidationError:
            response['is_available'] = False
        return Response(response)


class RegisterView(FormView):
    form_class = forms.RegisterForm
    template_name = 'fanart/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(RegisterView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        context['recaptcha_enabled'] = settings.RECAPTCHA_ENABLED
        return context

    def form_invalid(self, form):
        response = super(RegisterView, self).form_invalid(form)
        logger.info(f'Registration failed: {form.data} {form.errors.as_json()}')
        if self.request.is_ajax():
            ajax_response = {
                'success': False,
                'errors': form.errors,
            }
            return HttpResponse(json.dumps(ajax_response))
        else:
            return response

    # The form validates username and email, including uniqueness. Failures there are handled by form_invalid.
    # All other validations occur in form_valid.
    def form_valid(self, form):
        response = super(RegisterView, self).form_valid(form)

        # Check ReCAPTCHA
        if settings.RECAPTCHA_ENABLED:
            recaptcha_data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': self.request.POST.get('g-recaptcha-response')
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=recaptcha_data)
            result = r.json()
            if not result['success']:
                logger.info('ReCAPTCHA failure for {0} ({1}), ip {2}'.format(form.cleaned_data['username'].encode('utf8'), form.cleaned_data['email'], self.request.META['REMOTE_ADDR']))
                ajax_response = {
                    'success': False,
                    'errors': {'recaptcha': ['ReCAPTCHA failure. Please click the "I\'m not a robot" box.']},
                }
                return HttpResponse(json.dumps(ajax_response))

        # Check if entered passwords match
        password = form.cleaned_data['password']
        password_repeat = form.cleaned_data['password_repeat']
        if password != password_repeat:
            ajax_response = {
                'success': False,
                'errors': {'password': ['The passwords you entered did not match']},
            }
            return HttpResponse(json.dumps(ajax_response))

        # Check if password complexity requirements are met
        try:
            password_valid = password_validation.validate_password(password)
        except password_validation.ValidationError as errors:
            ajax_response = {
                'success': False,
                'errors': {'password': list(errors)},
            }
            return HttpResponse(json.dumps(ajax_response))

        # All tests pass; create the user
        m = hashlib.md5()
        m.update(password.encode())
        password_hash = m.hexdigest()
        user = models.User.objects.create_user(
            form.cleaned_data['username'],
            password=password_hash,
            email=form.cleaned_data['email'],
            is_artist=form.cleaned_data['is_artist']
        )
        login(self.request, user)
        logger.info(f'New user {user} created')

        # Add a historical artist name entry
        models.ArtistName.objects.create(artist=user, name=user.username)

        ajax_response = {
            'success': True,
        }
        return HttpResponse(json.dumps(ajax_response))

    def get_success_url(self):
        return reverse('artmanager:prefs')


class RecoveryView(TemplateView):
    template_name = 'fanart/recovery.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(RecoveryView, self).get(request, *args, **kwargs)


class UsernameAwarePasswordResetView(PasswordResetView):
    form_class = forms.UsernameAwarePasswordResetForm


class HashedPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = forms.HashedSetPasswordForm


# Bulletins/admin announcements

class AdminAnnouncementsView(TemplateView):
    template_name = 'includes/admin_announcements.html'

    def get_context_data(self, **kwargs):
        context = super(AdminAnnouncementsView, self).get_context_data(**kwargs)
        start = int(kwargs.get('start'))
        count = int(kwargs.get('count'))
        end = start + count
        context['admin_announcements'] = models.Bulletin.objects.filter(is_published=True, is_admin=True).order_by('-date_posted')[start:end]
        return context


class BulletinsView(TemplateView):
    template_name = 'includes/bulletins.html'

    def get_context_data(self, **kwargs):
        context = super(BulletinsView, self).get_context_data(**kwargs)
        start = int(kwargs.get('start'))
        count = int(kwargs.get('count'))
        end = start + count
        context['bulletins'] = models.Bulletin.objects.filter(is_published=True, is_admin=False).order_by('-date_posted')[start:end]
        return context


# Comments

class CommentsView(TemplateView):
    model = models.ThreadedComment
    template_name = 'includes/comments.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CommentsView, self).get_context_data(*args, **kwargs)
        picture = get_object_or_404(models.Picture, pk=kwargs['picture_id'])
        context['picture'] = picture
        context['comments'] = utils.tree_to_list(models.ThreadedComment.objects.filter(picture=picture), sort_by='date_posted', parent_field='reply_to')
        if self.request.user.is_authenticated:
            context['current_user_is_blocked'] = self.request.user.is_blocked_by(picture.artist) or self.request.user.is_blanket_blocked
        context['hash'] = uuid.uuid4()
        return context


class PostCommentView(LoginRequiredMixin, CreateView):
    model = models.ThreadedComment
    form_class = forms.ThreadedCommentForm
    template_name = 'includes/comments.html'

    def form_valid(self, form):
        logger.info(form.cleaned_data)
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.save()

        picture = form.cleaned_data['picture']
        if picture.artist.email_comments and self.request.user != picture.artist:
            email_context = {
                'user': self.request.user,
                'picture': picture,
                'comment': comment,
                'base_url': settings.SERVER_BASE_URL,
            }
            tasks.send_email.delay(
                recipients=[picture.artist.email],
                subject='TLKFAA: New Comment Posted',
                context=email_context,
                text_template='email/comment_posted.txt',
                html_template='email/comment_posted.html',
#                bcc=[settings.DEBUG_EMAIL]
            )

        logger.info('User {0} posted comment {1} ({2}).'.format(self.request.user, comment.id, picture))

        response = super(PostCommentView, self).form_valid(form)
        return response


class CommentDetailView(LoginRequiredMixin, DetailView):
    model = models.ThreadedComment
    form_class = forms.ThreadedCommentForm
    template_name = 'includes/comments.html'

    def get_object(self):
        return get_object_or_404(models.ThreadedComment, pk=self.kwargs['comment_id'], user=self.request.user)

    def get(self, request, *args, **kwargs):
        response = super(CommentDetailView, self).get(request, *args, **kwargs)
        if request.is_ajax():
            ajax_response = {
                'success': True,
                'comment': {
                    'comment': self.object.comment,
                }
            }
            return HttpResponse(json.dumps(ajax_response))
        else:
            return response


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = models.ThreadedComment
    form_class = forms.ThreadedCommentUpdateForm
    template_name = 'includes/comments.html'

    def get_object(self):
        return get_object_or_404(models.ThreadedComment, pk=self.kwargs['comment_id'], user=self.request.user)

    def form_valid(self, form):
        self.object.date_edited = timezone.now()
        return super(EditCommentView, self).form_valid(form)
#        return redirect('comments', picture_id=self.object.picture.id)

#    def get_context_data(self, *args, **kwargs):
#        context = super(EditCommentView, self).get_context_data(*args, **kwargs)
#        context['date_edited'] = self.object.date_edited
#        return context


class DeleteCommentView(LoginRequiredMixin, UpdateView):
    model = models.ThreadedComment
    form_class = forms.ThreadedCommentDeleteForm
    template_name = 'includes/comments.html'

    def get_object(self):
        return get_object_or_404(models.ThreadedComment, Q(user=self.request.user) | Q(picture__artist=self.request.user) | Q(bulletin__user=self.request.user), pk=self.kwargs['comment_id'])

    def form_valid(self, form):
        logger.info(f'{self.request.user} deleted comment {self.object}')
        self.object.is_deleted = True
        return super(DeleteCommentView, self).form_valid(form)
#        return self.object.get_absolute_url()
#        return redirect('comments', picture_id=self.object.picture.id)

#    def get_context_data(self, *args, **kwargs):
#        context = super(EditCommentView, self).get_context_data(*args, **kwargs)
#        context['date_edited'] = self.object.date_edited
#        return context


# Shouts (roars)

class ShoutsView(TemplateView):
    model = models.Shout
    template_name = 'includes/shouts.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ShoutsView, self).get_context_data(*args, **kwargs)
        artist = get_object_or_404(models.User, pk=kwargs['artist_id'])
        context['artist'] = artist
        start = int(self.request.GET.get('offset', 0))
        count = int(self.request.GET.get('count', 0))
        end = start + count
        context['shouts'] = artist.shouts_received.filter(reply_to__isnull=True).order_by('-date_posted')[start:end]
        shout_id = self.request.GET.get('shoutid', None)
        if shout_id:
            context['shouts'] = artist.shouts_received.filter(id=shout_id)
        if self.request.user.is_authenticated:
            context['current_user_is_blocked'] = self.request.user.is_blocked_by(artist) or self.request.user.is_blanket_blocked
        context['hash'] = uuid.uuid4()
        return context


class PostShoutView(LoginRequiredMixin, CreateView):
    model = models.Shout
    form_class = forms.ShoutForm
    template_name = 'includes/shouts.html'

    def form_valid(self, form):
        logger.info(form.cleaned_data)

        response = {'success': False}
        artist = form.cleaned_data['artist']
        if self.request.user.is_blocked_by(artist):
            raise PermissionDenied
        shout = form.save(commit=False)
        shout.user = self.request.user
        shout.save()

        if artist.email_shouts:
            email_context = {'user': self.request.user, 'artist': artist, 'shout': shout}
            tasks.send_email.delay(
                recipients=[artist.email],
                subject='TLKFAA: New Roar Posted',
                context=email_context,
                text_template='email/shout_posted.txt',
                html_template='email/shout_posted.html',
                bcc=[settings.DEBUG_EMAIL]
            )

        logger.info('User {0} posted shout {1} (artist {2}).'.format(self.request.user, shout.id, artist))

        response['shout_id'] = shout.id
        response['artist_id'] = shout.artist.id
        response['success'] = True
        return JsonResponse(response)


class ReplyShoutView(LoginRequiredMixin, CreateView):
    model = models.Shout
    form_class = forms.ShoutReplyForm
    template_name = 'includes/shouts.html'

    def post(self, *args, **kwargs):
        self.shout = get_object_or_404(models.Shout, pk=kwargs['shout_id'])
        return super().post(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        response = {'success': False}

        reply = form.save()
        reply.reply_to = self.shout
        reply.user = self.request.user
        reply.artist = self.shout.artist
        reply.save()
        response['shout_id'] = self.shout.id
        response['reply_id'] = reply.id

        response['success'] = True
        return JsonResponse(response)


class ShoutDetailView(LoginRequiredMixin, DetailView):
    model = models.Shout
    template_name = 'includes/shout.html'


class DeleteShoutView(LoginRequiredMixin, APIView):

    def post(self, request, shout_id):
        response = {'success': False}
        shout = get_object_or_404(models.Shout, Q(user=self.request.user) | Q(artist=self.request.user), pk=shout_id)
        shout.is_deleted = True
        shout.save()
        response['artist_id'] = shout.artist.id
        response['success'] = True
        return Response(response)


# Faves/blocks/visibility

class ToggleFaveView(APIView):

    def post(self, request, fave_type, object_id):
        response = {}
        if fave_type == 'picture':
            picture = get_object_or_404(models.Picture, pk=object_id)
            is_fave = True
            try:
                fave, is_created = models.Favorite.objects.get_or_create(user=request.user, picture=picture)
            except models.Favorite.MultipleObjectsReturned:
                fave = models.Favorite.objects.filter(user=request.user, picture=picture)
                is_created = False
                logger.info(f'Deleted multiple ({fave.count()}) faves')
            if is_created:
                logger.info(f'{request.user} favorited {picture}')
            else:
                logger.info(f'{request.user} unfavorited {picture}')
                fave.delete()
                is_fave = False
            response['picture_id'] = picture.id
            response['is_fave'] = is_fave
            picture.refresh_num_faves()
            picture.artist.refresh_num_faves()
        elif fave_type == 'artist':
            artist = get_object_or_404(models.User, pk=object_id, is_artist=True)
            is_fave = True
            try:
                fave, is_created = models.Favorite.objects.get_or_create(user=request.user, artist=artist)
            except models.Favorite.MultipleObjectsReturned:
                fave = models.Favorite.objects.filter(user=request.user, artist=artist)
                is_created = False
                logger.info(f'Deleted multiple ({fave.count()}) faves')
            if is_created:
                logger.info(f'{request.user} favorited {artist}')
            else:
                logger.info(f'{request.user} unfavorited {artist}')
                fave.delete()
                is_fave = False
            response['artist_id'] = artist.id
            response['is_fave'] = is_fave
            artist.refresh_num_faves()
        return Response(response)


class ToggleVisibleView(AjaxableResponseMixin, LoginRequiredMixin, UpdateView):
    model = models.Favorite
    form_class = forms.VisibleFaveForm

    def get_object(self):
        artist = get_object_or_404(models.User, pk=self.kwargs['artist_id'], is_artist=True)
        return get_object_or_404(models.Favorite, user=self.request.user, artist=artist)

    def get_success_url(self):
        return reverse('artist', kwargs={'dir_name': self.object.artist.dir_name})


class ToggleBlockView(APIView):

    def post(self, request, user_id):
        response = {}
        is_blocked = True
        blocked_user = get_object_or_404(models.User, pk=user_id)

        if blocked_user == self.request.user:
            response['success'] = True
            return Response(response)

        block, is_created = models.Block.objects.get_or_create(user=request.user, blocked_user=blocked_user)
        if not is_created:
            block.delete()
            is_blocked = False
        response['blocked_user_id'] = blocked_user.id
        response['is_blocked'] = is_blocked
        response['success'] = True
        return Response(response)


# Picture pages

class PictureRedirectByIDView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        picture_id = self.request.GET.get('pictureid')
        if not picture_id or not picture_id.isnumeric():
            raise Http404
        picture = get_object_or_404(models.Picture, pk=picture_id, date_deleted__isnull=True, artist__is_artist=True, artist__is_active=True)
        return reverse('picture', kwargs={'picture_id': picture.id})


class PictureRedirectByPathView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        picture = get_object_or_404(models.Picture, filename=kwargs.get('filename'), artist__dir_name=kwargs.get('dir_name'), date_deleted__isnull=True, artist__is_artist=True, artist__is_active=True)
        return picture.url


class PictureView(UserPaneMixin, TemplateView):
    template_name = 'fanart/picture.html'

    def get_context_data(self, **kwargs):
        context = super(PictureView, self).get_context_data(**kwargs)

        picture = get_object_or_404(models.Picture, pk=kwargs['picture_id'], date_deleted__isnull=True, artist__is_artist=True, artist__is_active=True)
        context['picture'] = picture
        context['picture_is_private'] = not picture.is_public and (not self.request.user.is_authenticated or picture.artist != self.request.user)
        context['comments'] = utils.tree_to_list(models.ThreadedComment.objects.filter(picture=picture), sort_by='date_posted', parent_field='reply_to')
        context['hash'] = uuid.uuid4()
        if self.request.user.is_authenticated:
            context['fave_artist'] = models.Favorite.objects.filter(artist=picture.artist, user=self.request.user).first()
            context['fave_picture'] = models.Favorite.objects.filter(picture=picture, user=self.request.user).first()
            context['current_user_is_blocked'] = self.request.user.is_blocked_by(picture.artist) or self.request.user.is_blanket_blocked

        logger.debug('{0} {1} viewing picture {2} via {3}'.format(self.request.user, self.request.META['REMOTE_ADDR'], picture, self.template_name))
        context['video_types'] = list(settings.MOVIE_FILE_TYPES.keys())
        return context


class PictureFansView(LoginRequiredMixin, DetailView):
    template_name = 'includes/picture_fans.html'

    def get_object(self):
        return get_object_or_404(models.Picture, pk=self.kwargs['picture_id'])


# Tooltip popup previews

class PictureTooltipView(PictureView):
    template_name = 'tooltips/picture.html'


class ColoringPictureTooltipView(TemplateView):
    template_name = 'tooltips/coloring_picture.html'

    def get_context_data(self, **kwargs):
        context = super(ColoringPictureTooltipView, self).get_context_data(**kwargs)
        coloring_picture = get_object_or_404(ColoringPicture, pk=kwargs['coloring_picture_id'])
        context['coloring_picture'] = coloring_picture
        return context


class MessageTooltipView(TemplateView):
    template_name = 'tooltips/message.html'

    def get_context_data(self, **kwargs):
        context = super(MessageTooltipView, self).get_context_data(**kwargs)

        context['max_width'] = settings.MAX_UPLOAD_WIDTH
        context['max_height'] = settings.MAX_UPLOAD_HEIGHT
        context['max_size'] = settings.MAX_UPLOAD_SIZE

        return context


# Characters

class CharacterView(UserPaneMixin, TemplateView):
    template_name = 'fanart/character.html'

    def get_context_data(self, **kwargs):
        context = super(CharacterView, self).get_context_data(**kwargs)

        context['character'] = get_object_or_404(models.Character, pk=kwargs.get('character_id', None))
        logger.info('{0} viewing character {1} via {2}'.format(self.request.user, context['character'], self.template_name))
        other_characters = self.request.GET.get('othercharacters', None)
        character_list = [str(context['character'].id)]
        if other_characters:
            context['other_characters'] = models.Character.objects.filter(id__in=other_characters.split(','))
            other_character_ids = [str(c.id) for c in context['other_characters']]
            context['other_characters_param'] = ','.join(other_character_ids)
            character_list += other_character_ids
            logger.info('Other characters: {0}'.format(character_list))
        context['canon_characters'] = models.Character.objects.filter(is_canon=True).order_by('name')

        character_pictures = models.Picture.objects.filter(artist__is_active=True)
        for character_id in character_list:
            character_pictures = character_pictures.filter(picturecharacter__character_id=character_id)
        context['character_pictures'] = character_pictures.order_by('-picturecharacter__date_tagged')

        return context


class CharacterTooltipView(CharacterView):
    template_name = 'tooltips/character.html'


# Artists

class ArtistView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artist.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)

        artist = get_object_or_404(models.User, is_artist=True, dir_name=kwargs['dir_name'])
        context['artist'] = artist
#        shouts_received = artist.shouts_received.order_by('-date_posted')
#        shouts_paginator = Paginator(shouts_received, 10)
#        context['shouts'] = shouts_paginator.page(1)
        context['shouts'] = artist.shouts_received.order_by('-date_posted')[0:10]

        context['last_nine_uploads'] = artist.picture_set.filter(is_public=True).order_by('-date_uploaded')[0:9]
        context['nine_most_popular_pictures'] = artist.picture_set.filter(num_faves__gt=0, is_public=True).order_by('-num_faves')[0:9]
        context['last_nine_coloring_pictures'] = artist.coloringpicture_set.filter(base__is_visible=True).order_by('-date_posted')[0:9]

        if self.request.user.is_authenticated:
            context['current_user_is_blocked'] = self.request.user.is_blocked_by(artist) or self.request.user.is_blanket_blocked
            context['fave_artist'] = models.Favorite.objects.filter(artist=artist, user=self.request.user).first()

        return context


class ArtistGalleryView(ArtistView):
    template_name = 'fanart/artist-gallery.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        artist = get_object_or_404(models.User, is_artist=True, dir_name=kwargs['dir_name'])
        context['artist'] = artist
        try:
            context['folder'] = models.Folder.objects.filter(pk=self.request.GET.get('folder_id', None), user=artist).first()
        except ValueError:
            raise Http404

        subview = kwargs.get('subview', None)
        if subview:
            context['show_folders'] = False
        else:
            context['show_folders'] = True
        context['list'] = self.request.GET.get('list', 'folder')

        if context['list'] == 'new' and self.request.user.is_authenticated:
            pictures = [uvp.picture for uvp in models.UnviewedPicture.objects.filter(picture__artist=artist, user=self.request.user).order_by('picture__date_uploaded')]
        else:
            pictures = artist.picture_set.all()

        if context['list'] == 'folder':
            pictures = pictures.filter(folder=context['folder']).order_by('date_uploaded')
        elif context['list'] == 'popular':
            pictures = pictures.order_by('num_faves')
        elif context['list'] == 'bydate':
            pictures = pictures.order_by('date_uploaded')

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

        context['pages_link'] = utils.PagesLink(len(pictures), settings.PICTURES_PER_PAGE, context['page_number'], is_descending=True, base_url=self.request.path, query_dict=self.request.GET)

        return context


class ArtWallView(ArtistView):
    template_name = 'fanart/artist-artwall.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        artist = get_object_or_404(models.User, is_artist=True, dir_name=kwargs['dir_name'])
        context['artist'] = artist

        gift_pictures = artist.gifts_received.order_by('picture__date_uploaded').filter(is_active=True, picture__is_public=True, picture__date_deleted__isnull=True)

        context['pictures_paginator'] = Paginator(gift_pictures, settings.PICTURES_PER_PAGE)
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

        context['pages_link'] = utils.PagesLink(gift_pictures.count(), settings.PICTURES_PER_PAGE, context['page_number'], is_descending=True, base_url=self.request.path, query_dict=self.request.GET)

        return context


class ColoringPicturesView(ArtistView):
    template_name = 'fanart/artist-coloringpictures.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        artist = get_object_or_404(models.User, is_artist=True, dir_name=kwargs['dir_name'])
        context['artist'] = artist

        pictures = artist.coloringpicture_set.order_by('-date_posted').all()

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

        context['pages_link'] = utils.PagesLink(len(pictures), settings.PICTURES_PER_PAGE, context['page_number'], is_descending=True, base_url=self.request.path, query_dict=self.request.GET)

        return context


# Artist of the Month

class AotmVoteView(LoginRequiredMixin, CreateView):
    template_name = 'includes/aotm_vote.html'
    form_class = forms.AotmVoteForm

    def form_valid(self, form):
        models.Vote.objects.filter(voter=self.request.user).delete()
        vote = form.save(commit=False)
        vote.voter = self.request.user
        vote.save()
        response = {
            'success': True,
            'username': form.cleaned_data['artist'].username,
        }
        return JsonResponse(response)

    def get_success_url(self):
        return reverse('aotm-vote')


class AotmVoteFormView(LoginRequiredMixin, TemplateView):
    template_name = 'includes/aotm_vote_form.html'


# Artist page support views

class FoldersView(APIView):
    permission_classes = ()

    def get(self, request, artist_id):
        response = {}

        artist = get_object_or_404(models.User, is_artist=True, id=artist_id)

        folders = []
        for folder in artist.folder_set.all():
            latest_picture = None
            if folder.latest_picture:
                latest_picture = {
                    'pictureid': folder.latest_picture.id,
                    'basename': folder.latest_picture.basename,
                    'extension': folder.latest_picture.extension,
                    'thumbheight': folder.latest_picture.thumb_height,
                    'uploaded': folder.latest_picture.date_uploaded.strftime('%-m/%-d/%Y'),
                    'preview_image_url': '{0}Artwork{1}{2}.p.{3}'.format(settings.MEDIA_URL, reverse('artist', kwargs={'dir_name': artist.dir_name}), folder.latest_picture.basename, folder.latest_picture.thumbnail_extension)
                }
            folders.append({
                'folderid': folder.id,
                'artistid': artist.id,
                'dirname': artist.dir_name,
                'name': folder.name,
                'description': folder.description,
                'parent': folder.parent_id,
                'numpictures': folder.picture_set.count(),
                'newpics': 0,
                'latestpicture': latest_picture,
                'url': '{0}?folder_id={1}'.format(reverse('artist-gallery', kwargs={'dir_name': artist.dir_name}), folder.id),
            })
        response['folders'] = folders

        return Response(response)


class ArtistsListView(ArtistsView):
    template_name = 'includes/artists-list.html'


class ArtworkListView(ArtworkView):
    template_name = 'includes/artwork-list.html'


# Characters page support views

class CharactersListView(CharactersView):
    template_name = 'includes/characters-list.html'


class CharactersSpeciesView(TemplateView):
    template_name = 'includes/species-list.html'

    def get_context_data(self, **kwargs):
        context = super(CharactersSpeciesView, self).get_context_data(**kwargs)

        characters = models.Character.objects.all()
        context['popular_species'] = []
        # Fill up the species box with a bunch of characters, sorted by popularity
        for species in characters.filter(owner__is_active=True).exclude(species='').values('species').annotate(num_characters=Count('species')).order_by('-num_characters')[0:20]:
            species['characters'] = characters.filter(species=species['species']).order_by('-num_pictures')[0:20]
            context['popular_species'].append(species)
        return context    


# Autocompletes

class CharactersAutocompleteView(APIView):
    permission_classes = ()

    def get(self, request, term):
        response = {'characters': []}

        for character in models.Character.objects.filter(name__icontains=term).order_by('-num_pictures')[0:20]:
            response['characters'].append({
                'name': character.name,
                'characterid': character.id,
                'artistname': getattr(character.owner, 'username', 'Canon'),
                'num_pictures': character.num_pictures,
            })

        return Response(response)


class SpeciesAutocompleteView(APIView):
    permission_classes = ()

    def get(self, request, term):
        response = {'specieses': []}

        for species in models.Character.objects.filter(species__icontains=term).values('species').annotate(num=Count('species')).order_by('-num')[0:20]:
            response['specieses'].append({
                'species': species['species'],
                'num': species['num'],
            })

        return Response(response)


class ArtistsAutocompleteView(APIView):
    permission_classes = ()

    def get(self, request, term):
        response = {'artists': []}

        startswith_queryset = models.User.objects.filter(is_artist=True, is_active=True, username__istartswith=term)
        contains_queryset = models.User.objects.filter(is_artist=True, is_active=True, username__icontains=term).exclude(username__istartswith=term)
        full_queryset = list(chain(startswith_queryset, contains_queryset))
        for artist in full_queryset[0:20]:
            response['artists'].append({
                'name': artist.username,
                'artistid': artist.id,
                'userid': artist.id,
                'dirname': artist.dir_name,
            })

        return Response(response)


# Pickers

class PicturePickerView(LoginRequiredMixin, TemplateView):
    template_name = 'includes/pick_picture.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PicturePickerView, self).get_context_data(*args, **kwargs)

#        folder_id = self.request.GET.get('folder_id', None)
#        selected_folder = models.Folder.objects.filter(user=self.request.user, pk=folder_id).first()

        folder_id = self.request.GET.get('folder_id', None)
        if folder_id == 'cc':
            pictures = self.request.user.coloringpicture_set.all()
            context['coloring_cave'] = True
        elif folder_id == 'artwall':
            pictures = self.request.user.gifts_received.all()
            context['artwall'] = True

        else:
            selected_folder = None
            if folder_id:
                try:
                    selected_folder = models.Folder.objects.get(pk=folder_id, user=self.request.user)
                except models.Folder.DoesNotExist:
                    pass

            sort_by = self.request.GET.get('sort_by', None)
            if not sort_by in ['newest', 'oldest', 'popularity', 'comments']:
                sort_by = 'newest'

            pictures = self.request.user.picture_set.all()

            if selected_folder:
                pictures = pictures.filter(folder=selected_folder)
            context['selected_folder'] = selected_folder

            if sort_by == 'newest':
                pictures = pictures.order_by('-date_uploaded')
            elif sort_by == 'oldest':
                pictures = pictures.order_by('date_uploaded')
            elif sort_by == 'popularity':
                pictures = pictures.order_by('-num_faves')
            elif sort_by == 'comments':
                pictures = pictures.order_by('-num_comments')
            context['sort_by'] = sort_by

        context['folders'] = utils.tree_to_list(self.request.user.folder_set.all(), sort_by='name')
        context['pictures'] = pictures

        return context


class CharacterPickerView(TemplateView):
    template_name = 'includes/pick_character.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CharacterPickerView, self).get_context_data(*args, **kwargs)
        context['characters'] = self.request.user.character_set.filter(date_deleted__isnull=True)
        return context


# Social media mgmt views -- ArtManager?

class SocialMediaIdentitiesView(TemplateView):
    template_name = 'includes/social_media.html'

    def get_context_data(self, **kwargs):
        context = super(SocialMediaIdentitiesView, self).get_context_data(**kwargs)

        context['social_medias'] = models.SocialMedia.objects.all()

        return context


class AddSocialMediaIdentityView(LoginRequiredMixin, CreateView):
    model = models.SocialMediaIdentity
    form_class = forms.SocialMediaIdentityForm

    def form_valid(self, form):
        identity = form.save(commit=False)
        identity.user = self.request.user
        identity.save()

        response = super(AddSocialMediaIdentityView, self).form_valid(form)
        return response

    def get_success_url(self):
        return reverse('social-media-identities', kwargs={})


class RemoveSocialMediaIdentityView(LoginRequiredMixin, DeleteView):
    model = models.SocialMediaIdentity

    def get_object(self):
        return get_object_or_404(models.SocialMediaIdentity, pk=self.kwargs['identity_id'], user=self.request.user)

    def get_success_url(self):
        return reverse('social-media-identities', kwargs={})


# Profile pic mgmt views -- ArtManager?

class UploadProfilePicView(LoginRequiredMixin, UpdateView):
    model = models.User
    form_class = forms.UploadProfilePicForm

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def get_object(self):
        user = self.request.user
        self.old_profile_picture = user.profile_picture
        self.old_profile_pic_thumbnail_path = user.profile_pic_thumbnail_path
        return user

    def form_invalid(self, form):
        response = {'success': False, 'errors': form.errors}
        logger.error(form.errors.as_data())
        return JsonResponse(response)

    def form_valid(self, form):
        response = {'success': False}

        logger.info(self.request.FILES)
#        self.object.picture = self.request.FILES['picture']
#        self.object.filename = self.request.FILES['picture'].name
#        self.object.date_uploaded = timezone.now()

        if not self.request.FILES['profile_picture'].content_type in list(settings.IMAGE_FILE_TYPES.keys()):
            response['errors'] = {
                'profile_picture': 'Invalid file type. Valid types are: {0}'.format(', '.join(list(settings.IMAGE_FILE_TYPES.values())))
            }
            return JsonResponse(response)

        try:
            if self.old_profile_picture:
                os.remove(self.old_profile_picture.path)
            if self.old_profile_pic_thumbnail_path:
                os.remove(self.old_profile_pic_thumbnail_path)
        except OSError:
            pass

#        super(UploadProfilePicView, self).form_valid(form)
        if self.object.profile_pic_id:
            self.object.profile_pic_id = None
            self.object.profile_pic_ext = ''

        self.object.save(update_thumbs=True)

        response['success'] = True
        return JsonResponse(response)

    def get_context_data(self, *args, **kwargs):
        context = super(UploadProfilePicView, self).get_context_data(*args, **kwargs)
        return context


class ProfilePicStatusView(APIView):

    def get(self, request):
        response = {}
        if request.user.profile_picture:
            response = {
                'url': request.user.profile_pic_url,
                'thumbnail_url': request.user.profile_pic_thumbnail_url,
                'thumbnail_done': request.user.profile_pic_thumbnail_created,
                'resize_done': request.user.profile_pic_resized,
            }
        return Response(response)


class RemoveProfilePicView(LoginRequiredMixin, UpdateView):
    model = models.User
    form_class = forms.RemoveProfilePicForm

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = {'success': True}

        logger.info(self.object.profile_picture.name)
        if self.object.profile_picture:
            try:
                os.remove(self.object.profile_picture.path)
                os.remove(self.object.profile_pic_thumbnail_path)
            except OSError:
                pass

        self.object.profile_picture = None
        self.object.profile_width = None
        self.object.profile_height = None
        self.object.save()

        return JsonResponse(response)


# Banner mgmt views -- ArtManager?

class UploadBannerView(LoginRequiredMixin, CreateView):
    model = models.Banner
    form_class = forms.UploadBannerForm

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def form_invalid(self, form):
        response = {'success': False}
        response['message'] = form.errors['picture'][0]
        return JsonResponse(response)

    def form_valid(self, form):
        response = {'success': False}

        if not form.cleaned_data['picture']:
            response['message'] = 'No picture was uploaded.'
            return JsonResponse(response)

        logger.info(self.request.FILES)
        logger.info(form.cleaned_data)
        logger.info(form.cleaned_data['picture'].size)
        if form.cleaned_data['picture'].size > settings.MAX_BANNER_SIZE:
            formatted_size = filesizeformat(settings.MAX_BANNER_SIZE)
            logger.info(formatted_size)
            response['message'] = 'File is too large. Please keep the file size under {0} for banner images.'.format(formatted_size)
            return JsonResponse(response)

        try:
            if self.request.user.banner:
                os.remove(self.request.user.banner.picture.path)
        except OSError:
            pass

        banner = form.save()
        logger.info(banner)
        self.request.user.banner = banner
        self.request.user.save()
        response['success'] = True

        return JsonResponse(response)

    def get_context_data(self, *args, **kwargs):
        context = super(UploadBannerView, self).get_context_data(*args, **kwargs)
        return context


class RemoveBannerView(LoginRequiredMixin, DeleteView):
    model = models.Banner

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def get_object(self):
        return self.request.user.banner

    def delete(self, request, *args, **kwargs):
        response = {'success': True}

        self.object = self.get_object()

        if not self.object:
            return JsonResponse(response)

        logger.info(self.object.picture.name)
        try:
            os.remove(self.object.picture.path)
        except OSError:
            pass

        self.request.user.banner = None
        self.request.user.save()
        self.object.delete()

        return JsonResponse(response)


# Bulletin mgmt views -- ArtManager?

class BulletinView(DetailView):
    model = models.Bulletin
    template_name = 'includes/bulletin.html'

    def get_context_data(self, **kwargs):
        context = super(BulletinView, self).get_context_data(**kwargs)
        context['comments'] = utils.tree_to_list(models.ThreadedComment.objects.filter(bulletin=self.object), sort_by='date_posted', parent_field='reply_to')
        context['hash'] = uuid.uuid4()
        return context

    def get_object(self):
        return get_object_or_404(models.Bulletin, pk=self.kwargs['bulletin_id'], is_published=True)


class PostBulletinReplyView(LoginRequiredMixin, CreateView):
    model = models.ThreadedComment
    form_class = forms.ThreadedCommentForm
    template_name = 'includes/comments.html'

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])

    def form_valid(self, form):
        logger.info(form.cleaned_data)
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.save()

        bulletin = form.cleaned_data['bulletin']
        if bulletin.user.email_comments and self.request.user != bulletin.user:
            email_context = {
                'user': self.request.user,
                'bulletin': bulletin,
                'comment': comment,
                'base_url': settings.SERVER_BASE_URL,
            }
            tasks.send_email.delay(
                recipients=[bulletin.user.email],
                subject='TLKFAA: New Bulletin Reply Posted',
                context=email_context,
                text_template='email/bulletin_comment_posted.txt',
                html_template='email/bulletin_comment_posted.html',
#                bcc=[settings.DEBUG_EMAIL]
            )

        logger.info('User {0} posted bulletin comment {1} ({2}).'.format(self.request.user, comment.id, bulletin.id))

        response = super(PostBulletinReplyView, self).form_valid(form)
        return response


# Boilerplate site static pages

class GuidelinesView(TemplateView):
    template_name = 'includes/guidelines.html'


class AboutView(TemplateView):
    template_name = 'fanart/about.html'


class TermsOfServiceView(TemplateView):
    template_name = 'fanart/terms_of_service.html'


class PrivacyView(TemplateView):
    template_name = 'fanart/privacy.html'


class HelpView(TemplateView):
    template_name = 'fanart/help.html'


class BrowserStatsView(APIView):
    permission_classes = ()

    def post(self, request):
        response = {}
        models.BrowserStats.objects.create(
            width=request.data['width'],
            height=request.data['height'],
            user=request.user if request.user.is_authenticated else None,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        return Response(response)
