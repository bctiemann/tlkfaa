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

from fanart import models, forms, utils, tasks

from .response import JSONResponse, response_mimetype
from .serialize import serialize

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


class LoginView(LoginView):
    form_class = forms.LoginForm


class UserPaneMixin(object):

    def get_community_art_data(self):
        community_art_data = {}
        icons_publish_start_date = timezone.now() - timedelta(weeks=3)
        adoptables_publish_start_date = timezone.now() - timedelta(days=30*6)
        adoptables_mine_start_date = timezone.now() - timedelta(days=30)
        community_art_data['icons'] = models.TradingOffer.objects.filter(type='icon', is_active=True, is_visible=True, date_posted__gt=icons_publish_start_date)
        community_art_data['icons_today'] = models.TradingOffer.objects.filter(type='icon', is_active=True, is_visible=True, date_posted__date__gte=timezone.now())
        if self.request.user.is_authenticated:
            community_art_data['icons_mine'] = models.TradingClaim.objects.filter(offer__type='icon', offer__is_active=True, offer__is_visible=True, date_fulfilled__isnull=True, filename='', offer__date_posted__gt=icons_publish_start_date, user=self.request.user)
        community_art_data['adoptables'] = models.TradingOffer.objects.filter(type='adoptable', is_active=True, is_visible=True, date_posted__gt=adoptables_publish_start_date)
        community_art_data['adoptables_unclaimed'] = community_art_data['adoptables'].filter(adopted_by__isnull=True)
        if self.request.user.is_authenticated:
            community_art_data['adoptables_mine'] = models.TradingClaim.objects.filter(offer__type='adoptable', offer__is_active=True, offer__is_visible=True, date_fulfilled__isnull=False, offer__date_posted__gt=adoptables_mine_start_date, user=self.request.user)
        community_art_data['coloring_bases'] = models.ColoringBase.objects.filter(is_active=True, is_visible=True)
        return community_art_data

    def get_contests_data(self):
        contests_data = {}
        contests_data['contests_new'] = models.Contest.objects.filter(type='personal', is_active=True, is_cancelled=False, date_end__gt=timezone.now()).order_by('-date_start')[0:5]
        contests_data['contests_ending'] = models.Contest.objects.filter(type='personal', is_active=True, is_cancelled=False, date_end__gt=timezone.now()).order_by('-date_end')[0:5]
        return contests_data


class UserPaneView(UserPaneMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super(UserPaneView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        return context


class HomeView(UserPaneMixin, TemplateView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        context['current_contest'] = models.Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()
        context['admin_announcements'] = [models.Bulletin.objects.filter(is_published=True, is_admin=True).order_by('-date_posted').first()]
        context['bulletins'] = models.Bulletin.objects.filter(is_published=True, is_admin=False).order_by('-date_posted')[0:5]
        context['recently_active_artists'] = models.User.objects.recently_active()
        return context


class ArtistsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artists.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistsView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        context['show_search_input'] = False

        list = kwargs.get('list', self.request.GET.get('list', settings.DEFAULT_ARTISTS_VIEW))
        if not list in ['name', 'newest', 'recentactive', 'toprated', 'topratedactive', 'prolific', 'random', 'search']:
            list = settings.DEFAULT_ARTISTS_VIEW

        start = int(self.request.GET.get('start', 0))
        initial = self.request.GET.get('initial', None)

        artists = models.User.objects.filter(is_active=True, is_artist=True, num_pictures__gt=0)
        one_month_ago = timezone.now() - timedelta(days=180)
        if list == 'name':
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
        elif list == 'newest':
            artists = artists.order_by('-date_joined')
        elif list == 'recentactive':
            artists = artists.order_by('-last_upload')
        elif list == 'toprated':
            artists = artists.extra(select={'rating': 'num_favepics / num_pictures * num_faves'}).order_by('-rating')
        elif list == 'topratedactive':
            artists = artists.filter(last_upload__gt=one_month_ago).extra(select={'rating': 'num_favepics / num_pictures * num_faves'}).order_by('-rating')
        elif list == 'prolific':
            artists = artists.order_by('-num_pictures')
        elif list == 'random':
            artists = artists.order_by('?')
        elif list == 'search':
            term = self.request.GET.get('term', None)
            if not term:
                context['show_search_input'] = True
            if term:
                context['term'] = term
                artists = artists.filter(username__icontains=term).order_by('sort_name')
            else:
                artists = artists.filter(id__isnull=True)

        context['list'] = list
        context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['initial'] = initial
        context['artists'] = artists[start:start + context['count']]
        if list == 'name':
            context['artists'] = artists_page
            context['count'] = None
            context['pages_link'] = utils.PagesLink(len(artists), settings.ARTISTS_PER_PAGE_INITIAL, artists_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        return context


class ArtworkView(UserPaneMixin, TemplateView):
    template_name = 'fanart/artwork.html'

    def get_context_data(self, **kwargs):
        context = super(ArtworkView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        context['show_search_input'] = False

        default_artwork_view = settings.DEFAULT_ARTWORK_VIEW
        if self.request.user.is_authenticated() and self.request.user.unviewedpicture_set.exists():
            default_artwork_view = 'unviewed'

#        mode = kwargs.get('mode', None)
#        if not mode in ['canon', 'fan', 'mosttagged', 'recentlytagged', 'charactername'] and not dir_name:
#            mode = 'canon'

        list = kwargs.get('list', self.request.GET.get('list', default_artwork_view))
        if not list in ['unviewed', 'newest', 'newestfaves', 'toprated', 'topratedrecent', 'random', 'search', 'tag', 'character']:
            list = default_artwork_view

        start = int(self.request.GET.get('start', 0))
        initial = self.request.GET.get('initial', None)

        artwork = models.Picture.objects.filter(artist__is_active=True, artist__is_artist=True, artist__num_pictures__gt=0)
        three_months_ago = timezone.now() - timedelta(days=THREE_MONTHS)
        one_month_ago = timezone.now() - timedelta(days=ONE_MONTH)
        if list == 'unviewed':
            artwork = [uvp.picture for uvp in models.UnviewedPicture.objects.filter(user=self.request.user).order_by('-picture__date_uploaded')]
        elif list == 'newest':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago).order_by('-date_uploaded')
        elif list == 'newestfaves':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago, artist__in=Subquery(self.request.user.favorite_set.filter(picture__isnull=True).values('artist_id'))).order_by('-date_uploaded')
            logger.info(artwork.query)
        elif list == 'toprated':
            artwork = artwork.filter(num_faves__gt=100).order_by('-num_faves')
        elif list == 'topratedrecent':
            artwork = artwork.filter(date_uploaded__gt=three_months_ago).order_by('-num_faves')
        elif list == 'prolific':
            artists = artists.order_by('-num_pictures')
        elif list == 'random':
            random_ids = random.sample(range(models.Picture.objects.all().aggregate(Min('id'))['id__min'], models.Picture.objects.all().aggregate(Max('id'))['id__max']), 100)
            artwork = artwork.filter(pk__in=random_ids)
        elif list in ['search', 'tag', 'character']:
            term = self.request.GET.get('term', None)
            if not term:
                context['show_search_input'] = True
                context['top_300_tags'] = sorted(models.Tag.objects.annotate(num_pictures=Count('picture')).order_by('-num_pictures')[:300], key=lambda tag: tag.tag)
            if term:
                context['term'] = term
                if list == 'search':
                    artwork = artwork.filter(title__icontains=term).order_by('-num_faves')
                elif list == 'tag':
                    logger.info(term)
                    tag = models.Tag.objects.filter(tag=term).first()
                    logger.info(tag)
                    if tag:
                        artwork = tag.picture_set.all().order_by('-num_faves')
                    else:
                        artwork = artwork.filter(id__isnull=True)
                elif list == 'character':
                    character_pictures = models.Picture.objects.all()
                    for character_id in term.split(','):
                        character_pictures = character_pictures.filter(picturecharacter__character_id=character_id)
                        artwork = character_pictures.order_by('-picturecharacter__date_tagged')
            else:
                artwork = artwork.filter(id__isnull=True)

        context['list'] = list
        context['count'] = int(self.request.GET.get('count', settings.ARTISTS_PER_PAGE))
        context['next_start'] = start + settings.ARTISTS_PER_PAGE
        context['initial'] = initial
        context['artwork'] = artwork[start:start + context['count']]

        return context


class CharactersView(UserPaneMixin, TemplateView):
    template_name = 'fanart/characters.html'

    def get_context_data(self, **kwargs):
        context = super(CharactersView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        dir_name = kwargs.get('dir_name', None)
        if dir_name:
            context['artist'] = get_object_or_404(models.User, is_artist=True, dir_name=dir_name)

        mode = kwargs.get('mode', None)
        if not mode in ['canon', 'fan', 'mosttagged', 'recentlytagged', 'charactername'] and not dir_name:
            mode = 'canon'

        characters = models.Character.objects.all()
        if dir_name:
            characters = characters.filter(owner=context['artist']).order_by('name')
        elif mode == 'canon':
            characters = characters.filter(is_canon=True).order_by('-num_pictures')
        elif mode == 'fan':
            term = self.request.GET.get('term', None)
            match_type = self.request.GET.get('match', 'contains')
            if term:
                list = self.request.GET.get('list', None)
                if not list in ['artist', 'species', 'charactername']:
                    list = 'charactername'
                characters = characters.filter(owner__is_active=True).order_by('name')
                if list == 'artist':
                    characters = characters.filter(owner__id=term)
                elif list == 'species':
                    if match_type == 'exact':
                        characters = characters.filter(species=term)
                    else:
                        characters = characters.filter(species__icontains=term)
                elif list == 'charactername':
                    if match_type == 'exact':
                        characters = characters.filter(name=term)
                    else:
                        characters = characters.filter(name__icontains=term)
            else:
                context['popular_species'] = characters.filter(owner__is_active=True).exclude(species='').values('species').annotate(num_characters=Count('species')).order_by('-num_characters')[0:50]
                characters = characters.filter(id__isnull=True)
        elif mode == 'mosttagged':
            characters = characters.filter(num_pictures__gt=0).order_by('-num_pictures')
        elif mode == 'recentlytagged':
            characters = characters.filter(num_pictures__gt=0).order_by('-date_tagged')

        context['characters_paginator'] = Paginator(characters, settings.CHARACTERS_PER_PAGE)
        try:
            page = int(self.request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            characters_page = context['characters_paginator'].page(page)
        except EmptyPage:
            characters_page = context['characters_paginator'].page(1)

        context['mode'] = mode
        context['characters'] = characters_page
        context['pages_link'] = utils.PagesLink(len(characters), settings.CHARACTERS_PER_PAGE, characters_page.number, is_descending=False, base_url=self.request.path, query_dict=self.request.GET)

        return context


class TradingTreeView(UserPaneMixin, TemplateView):
    template_name = 'fanart/tradingtree.html'

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
            context['offer'] = get_object_or_404(models.TradingOffer, pk=offer_id)
            if self.request.user.is_authenticated():
                context['my_claims_for_offer'] = context['offer'].tradingclaim_set.filter(user=self.request.user)

        three_months_ago = timezone.now() - timedelta(days=THREE_MONTHS)
        context['offers'] = models.TradingOffer.objects.filter(is_visible=True, is_active=True, type=offer_type, date_posted__gt=three_months_ago).order_by('-date_posted')

        if self.request.user.is_authenticated() and ((offer_type == 'icon' and self.request.user.icon_claims_ready.exists()) or (offer_type == 'adoptable' and self.request.user.adoptable_claims_ready.exists())):
            context['show_for_you'] = True
            if offer_type == 'icon':
                context['claims_for_you'] = self.request.user.icon_claims_ready.all()
            elif offer_type == 'adoptable':
                context['claims_for_you'] = self.request.user.adoptable_claims_ready.all()

        context['offer_type'] = offer_type
        return context


class ColoringCaveView(UserPaneMixin, TemplateView):
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
            context['coloring_base'] = get_object_or_404(models.ColoringBase, pk=coloring_base_id)
        else:
            coloring_bases = models.ColoringBase.objects.filter(is_visible=True)
            if sort_by == 'popularity':
                coloring_bases = coloring_bases.order_by('-num_colored')
            elif sort_by == 'date':
                coloring_bases = coloring_bases.order_by('-date_posted')

            context['coloring_bases'] = coloring_bases[0:100]
        context['sort_by'] = sort_by

        return context


class ColoringCavePictureView(UserPaneMixin, TemplateView):
    template_name = 'fanart/coloringcave.html'

    def get_context_data(self, **kwargs):
        context = super(ColoringCavePictureView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        context['coloring_bases'] = coloring_bases[0:100]
        context['sort_by'] = sort_by

        return context


class SpecialFeaturesView(UserPaneMixin, TemplateView):
    template_name = 'fanart/special.html'

    def get_context_data(self, **kwargs):
        context = super(SpecialFeaturesView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        special_id = kwargs.get('special_id', None)

        if special_id:
            context['special'] = get_object_or_404(models.SpecialFeature, pk=special_id)

            pictures = context['special'].pictures.order_by('date_uploaded')

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

            context['specials'] = models.SpecialFeature.objects.filter(is_visible=True).order_by('id')

        return context


class ContestsView(UserPaneMixin, TemplateView):
    template_name = 'fanart/contests.html'

    def get_context_data(self, **kwargs):
        context = super(ContestsView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        sort_by = self.request.GET.get('sort_by', None)
        if not sort_by in ['artist', 'startdate', 'deadline']:
            sort_by = 'startdate'

        contest_id = kwargs.get('contest_id', None)
        if contest_id:
            context['contest'] = get_object_or_404(models.Contest, pk=contest_id)
        else:
            contest_type = kwargs.get('contest_type', None)
            if not contest_type:
                contest_type = 'global'

            personal_account_deadline_cutoff_date = timezone.now() - timedelta(days=2)
            contests = models.Contest.objects.filter(type=contest_type, is_active=True)
            if contest_type == 'personal':
                contests = contests.filter(date_end__gte=personal_account_deadline_cutoff_date)

            if sort_by == 'artist':
                contests = contests.order_by('creator__username')
            if sort_by == 'startdate':
                contests = contests.order_by('-date_start')
            if sort_by == 'deadline':
                contests = contests.order_by('-date_end')

            context['contests'] = contests

        context['sort_by'] = sort_by

        return context


class ContestView(UserPaneMixin, DetailView):
    model = models.Contest
    form_class = forms.ContestEntryForm
    template_name = 'fanart/contest.html'

    def get_object(self):
        return get_object_or_404(models.Contest, pk=self.kwargs['contest_id'])

    def get_context_data(self, **kwargs):
        context = super(ContestView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        context['my_vote'] = models.ContestVote.objects.filter(user=self.request.user, entry__contest=self.object).first()

#        logger.info(context['form'])
        logger.info(self.object)

        return context


class ContestEntryCreateView(CreateView):
    model = models.ContestEntry
    form_class = forms.ContestEntryForm
    template_name = 'fanart/contest.html'

    def form_valid(self, form):
        contest = get_object_or_404(models.Contest, pk=self.kwargs.get('contest_id', None))
        picture = get_object_or_404(models.Picture, pk=self.request.POST.get('picture', None), artist=self.request.user)

        contest_entry = form.save(commit=False)
        contest_entry.user = self.request.user
        contest_entry.contest = contest
        contest_entry.picture = picture
        contest_entry.save()
        response = super(ContestEntryCreateView, self).form_valid(form)
        return response


class ContestEntryDeleteView(DeleteView):
    model = models.ContestEntry

    def get_object(self):
        return get_object_or_404(models.ContestEntry, (Q(picture__artist=self.request.user) | Q(contest__creator=self.request.user)), pk=self.kwargs['entry_id'])

    def form_valid(self, form):
        response = super(ContestEntryDeleteView, self).form_valid(form)
        return response

    def get_success_url(self):
        return reverse('contest', kwargs={'contest_id': self.object.contest.id})


class ContestVoteView(CreateView):
    model = models.ContestVote
    form_class = forms.ContestVoteForm
    template_name = 'fanart/contest.html'

    def form_valid(self, form):
        models.ContestVote.objects.filter(entry__contest=form.cleaned_data['entry'].contest, user=self.request.user).delete()

        contest_vote = form.save(commit=False)
        contest_vote.user = self.request.user
        contest_vote.save()

        response = super(ContestVoteView, self).form_valid(form)
        return response


class FavoritePicturesView(UserPaneMixin, TemplateView):
    template_name = 'fanart/favorite_pictures.html'

    def get_context_data(self, **kwargs):
        context = super(FavoritePicturesView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        if not self.request.user.is_authenticated():
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


class GuidelinesView(TemplateView):
    template_name = 'includes/guidelines.html'


class UserBoxSetView(APIView):

    def get(self, request, box=None, show=None):
        response = {}
        if box in ('favorite_artists_box', 'favorite_pictures_box', 'sketcher_box', 'community_art_box', 'contests_box', 'tool_box',):
            request.session[box] = True if show == '1' else False
        return Response(response)


class FavoriteArtistsBoxView(UserPaneView):
    template_name = 'fanart/userpane/favorite_artists.html'

class FavoritePicturesBoxView(UserPaneView):
    template_name = 'fanart/userpane/favorite_pictures.html'

class SketcherBoxView(UserPaneView):
    template_name = 'fanart/userpane/sketcher.html'

class CommunityArtBoxView(UserPaneView):
    template_name = 'fanart/userpane/community_art.html'

    def get_context_data(self, **kwargs):
        context = super(CommunityArtBoxView, self).get_context_data(**kwargs)
        context['community_art_data'] = self.get_community_art_data()
        return context

class ContestsBoxView(UserPaneView):
    template_name = 'fanart/userpane/contests.html'

    def get_context_data(self, **kwargs):
        context = super(ContestsBoxView, self).get_context_data(**kwargs)
        context['contests_data'] = self.get_contests_data()
        return context

class ToolBoxView(UserPaneView):
    template_name = 'fanart/userpane/toolbox.html'


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


class CommentsView(TemplateView):
    model = models.PictureComment
    template_name = 'includes/comments.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CommentsView, self).get_context_data(*args, **kwargs)
        picture = get_object_or_404(models.Picture, pk=kwargs['picture_id'])
        context['picture'] = picture
        context['comments'] = utils.tree_to_list(models.PictureComment.objects.filter(picture=picture), sort_by='date_posted', parent_field='reply_to')
        context['current_user_is_blocked'] = models.Block.objects.filter(blocked_user=self.request.user, user=picture.artist).exists()
        context['hash'] = uuid.uuid4()
        return context


class PostCommentView(CreateView):
    model = models.PictureComment
    form_class = forms.PictureCommentForm

    def form_valid(self, form):
        logger.info(form.cleaned_data)
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.save()
        response = super(PostCommentView, self).form_valid(form)
        return response


class CommentDetailView(DetailView):
    model = models.PictureComment
    form_class = forms.PictureCommentForm
    template_name = 'includes/comments.html'

    def get_object(self):
        return get_object_or_404(models.PictureComment, pk=self.kwargs['comment_id'], user=self.request.user)

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


class EditCommentView(UpdateView):
    model = models.PictureComment
    form_class = forms.PictureCommentUpdateForm
    template_name = 'includes/comments.html'

    def get_object(self):
        return get_object_or_404(models.PictureComment, pk=self.kwargs['comment_id'], user=self.request.user)

    def form_valid(self, form):
        self.object.date_edited = timezone.now()
        super(EditCommentView, self).form_valid(form)
        return redirect('comments', picture_id=self.object.picture.id)

#    def get_context_data(self, *args, **kwargs):
#        context = super(EditCommentView, self).get_context_data(*args, **kwargs)
#        context['date_edited'] = self.object.date_edited
#        return context


class DeleteCommentView(UpdateView):
    model = models.PictureComment
    form_class = forms.PictureCommentDeleteForm
    template_name = 'includes/comments.html'

    def get_object(self):
        logger.info('get_object')
        return get_object_or_404(models.PictureComment, Q(user=self.request.user) | Q(picture__artist=self.request.user), pk=self.kwargs['comment_id'])

    def form_valid(self, form):
        logger.info('delete')
        self.object.is_deleted = True
        super(DeleteCommentView, self).form_valid(form)
        return redirect('comments', picture_id=self.object.picture.id)

#    def get_context_data(self, *args, **kwargs):
#        context = super(EditCommentView, self).get_context_data(*args, **kwargs)
#        context['date_edited'] = self.object.date_edited
#        return context


class ShoutsView(TemplateView):
    model = models.Shout
    template_name = 'includes/shouts.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ShoutsView, self).get_context_data(*args, **kwargs)
        artist = get_object_or_404(models.User, pk=kwargs['artist_id'])
        context['artist'] = artist
        offset = self.request.GET.get('offset', 0)
        context['shouts'] = artist.shouts_received.order_by('-date_posted')[offset:]
        shout_id = self.request.GET.get('shoutid', None)
        if shout_id:
            context['shouts'] = context['shouts'].filter(id=shout_id)
        context['current_user_is_blocked'] = models.Block.objects.filter(blocked_user=self.request.user, user=artist).exists()
        context['hash'] = uuid.uuid4()
        return context


class PostShoutView(CreateView):
    model = models.Shout
    form_class = forms.ShoutForm
    template_name = 'includes/shouts.html'

    def form_valid(self, form):
        response = {'success': False}
        artist = models.User.objects.get(pk=self.request.POST.get('artist', None))
        current_user_is_blocked = models.Block.objects.filter(blocked_user=self.request.user, user=artist).exists()
        if current_user_is_blocked:
            raise PermissionDenied
        shout = form.save(commit=False)
        shout.user = self.request.user
        shout.save()

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


class DeleteShoutView(APIView):

    def post(self, request, shout_id):
        response = {'success': False}
        shout = get_object_or_404(models.Shout, Q(user=self.request.user) | Q(artist=self.request.user), pk=shout_id)
        shout.is_deleted = True
        shout.save()
        response['artist_id'] = shout.artist.id
        response['success'] = True
        return Response(response)


class ToggleFaveView(APIView):

    def get(self, request, fave_type, object_id):
        response = {}
        if fave_type == 'picture':
            picture = get_object_or_404(models.Picture, pk=object_id)
            is_fave = True
            fave, is_created = models.Favorite.objects.get_or_create(user=request.user, picture=picture)
            if not is_created:
                fave.delete()
                is_fave = False
            response['picture_id'] = picture.id
            response['is_fave'] = is_fave
        elif fave_type == 'artist':
            artist = get_object_or_404(models.User, pk=object_id, is_artist=True)
            is_fave = True
            fave, is_created = models.Favorite.objects.get_or_create(user=request.user, artist=artist)
            if not is_created:
                fave.delete()
                is_fave = False
            response['artist_id'] = artist.id
            response['is_fave'] = is_fave
        return Response(response)


class ToggleBlockView(APIView):

    def post(self, request, user_id):
        response = {}
        is_blocked = True
        blocked_user = get_object_or_404(models.User, pk=user_id)
        block, is_created = models.Block.objects.get_or_create(user=request.user, blocked_user=blocked_user)
        if not is_created:
            block.delete()
            is_blocked = False
        response['blocked_user_id'] = blocked_user.id
        response['is_blocked'] = is_blocked
        return Response(response)


class PictureView(TemplateView):
    template_name = 'fanart/picture.html'

    def get_context_data(self, **kwargs):
        context = super(PictureView, self).get_context_data(**kwargs)
        picture = get_object_or_404(models.Picture, pk=kwargs['picture_id'])
        context['picture'] = picture
        context['picture_is_private'] = not picture.is_public and (not self.request.user.is_authenticated or picture.artist != self.request.user)
        context['comments'] = utils.tree_to_list(models.PictureComment.objects.filter(picture=picture), sort_by='date_posted', parent_field='reply_to')
        context['hash'] = uuid.uuid4()
        if self.request.user.is_authenticated():
            context['fave_artist'] = models.Favorite.objects.filter(artist=picture.artist, user=self.request.user).first()
            context['fave_picture'] = models.Favorite.objects.filter(picture=picture, user=self.request.user).first()
            context['current_user_is_blocked'] = models.Block.objects.filter(blocked_user=self.request.user, user=picture.artist).exists()

        context['video_types'] = [
            'video/quicktime',
            'video/mpeg',
            'video/mp4',
            'video/x-msvideo',
            'video/x-ms-wmv',
        ]
        return context


class PictureTooltipView(PictureView):
    template_name = 'includes/tooltip_picture.html'

class ColoringPictureTooltipView(TemplateView):
    template_name = 'includes/tooltip_coloring_picture.html'

    def get_context_data(self, **kwargs):
        context = super(ColoringPictureTooltipView, self).get_context_data(**kwargs)
        coloring_picture = get_object_or_404(models.ColoringPicture, pk=kwargs['coloring_picture_id'])
        context['coloring_picture'] = coloring_picture
        return context

class MessageTooltipView(TemplateView):
    template_name = 'includes/tooltip_message.html'

    def get_context_data(self, **kwargs):
        context = super(MessageTooltipView, self).get_context_data(**kwargs)

        context['max_width'] = settings.MAX_UPLOAD_WIDTH
        context['max_height'] = settings.MAX_UPLOAD_HEIGHT
        context['max_size'] = settings.MAX_UPLOAD_SIZE

        return context


class CharacterView(TemplateView):
    template_name = 'fanart/character.html'

    def get_context_data(self, **kwargs):
        context = super(CharacterView, self).get_context_data(**kwargs)

        context['character'] = get_object_or_404(models.Character, pk=kwargs.get('character_id', None))
        other_characters = self.request.GET.get('othercharacters', None)
        character_list = [str(context['character'].id)]
        if other_characters:
            context['other_characters'] = models.Character.objects.filter(id__in=other_characters.split(','))
            other_character_ids = [str(c.id) for c in context['other_characters']]
            context['other_characters_param'] = ','.join(other_character_ids)
            character_list += other_character_ids
        context['canon_characters'] = models.Character.objects.filter(is_canon=True).order_by('name')
        logger.info(character_list)

        character_pictures = models.Picture.objects.all()
        for character_id in character_list:
            character_pictures = character_pictures.filter(picturecharacter__character_id=character_id)
        context['character_pictures'] = character_pictures.order_by('-picturecharacter__date_tagged')

        return context


class ArtistView(TemplateView):
    template_name = 'fanart/artist.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        artist = get_object_or_404(models.User, is_artist=True, dir_name=kwargs['dir_name'])
        context['artist'] = artist
#        shouts_received = artist.shouts_received.order_by('-date_posted')
#        shouts_paginator = Paginator(shouts_received, 10)
#        context['shouts'] = shouts_paginator.page(1)
        context['shouts'] = artist.shouts_received.order_by('-date_posted')[0:10]
        context['current_user_is_blocked'] = models.Block.objects.filter(blocked_user=self.request.user, user=artist).exists()

        context['last_nine_uploads'] = artist.picture_set.filter(is_public=True).order_by('-date_uploaded')[0:9]
        context['nine_most_popular_pictures'] = artist.picture_set.filter(num_faves__gt=0, is_public=True).order_by('-num_faves')[0:9]
        context['last_nine_coloring_pictures'] = artist.coloringpicture_set.filter(base__is_visible=True).order_by('-date_posted')[0:9]

        if self.request.user.is_authenticated():
            context['fave_artist'] = models.Favorite.objects.filter(artist=artist, user=self.request.user).first()

        return context


class ArtistGalleryView(ArtistView):
    template_name = 'fanart/artist-gallery.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        artist = get_object_or_404(models.User, is_artist=True, dir_name=kwargs['dir_name'])
        context['artist'] = artist
        context['folder'] = models.Folder.objects.filter(pk=self.request.GET.get('folder_id', None)).first()

        subview = kwargs.get('subview', None)
        if subview:
            context['show_folders'] = False
        else:
            context['show_folders'] = True
        context['list'] = self.request.GET.get('list', 'folder')

        if context['list'] == 'new' and self.request.user.is_authenticated():
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

        pictures = [gp.picture for gp in artist.gifts_received.order_by('picture__date_uploaded').filter(is_active=True, picture__is_public=True, picture__date_deleted__isnull=True)]

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


class FoldersView(APIView):

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
                    'preview_image_url': '{0}Artwork{1}{2}.p.jpg'.format(settings.MEDIA_URL, reverse('artist', kwargs={'dir_name': artist.dir_name}), folder.latest_picture.basename)
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

        for species in models.Character.objects.filter(species__icontains=term).values('species').annotate(num=Count('species'))[0:20]:
            response['specieses'].append({
                'species': species['species'],
                'num': species['num'],
            })

        return Response(response)


class ArtistsAutocompleteView(APIView):
    permission_classes = ()

    def get(self, request, term):
        response = {'artists': []}

        for artist in models.User.objects.filter(is_artist=True, is_active=True, username__icontains=term)[0:20]:
            response['artists'].append({
                'name': artist.username,
                'artistid': artist.id,
                'userid': artist.id,
                'dirname': artist.dir_name,
            })

        return Response(response)


class PostClaimView(CreateView):
    model = models.TradingClaim
    form_class = forms.ClaimForm
    template_name = 'includes/tradingtree.html'

    def form_valid(self, form):
        logger.info(self.request.POST)
        response = {'success': False}
        offer = models.TradingOffer.objects.get(pk=self.request.POST.get('offer', None))

        claim = form.save(commit=False)
        claim.offer = offer
        claim.user = self.request.user
        claim.save()

        return JsonResponse(response)


class UploadClaimView(UpdateView):
    model = models.TradingClaim
    form_class = forms.UploadClaimForm
    template_name = 'includes/claim.html'

    def get_object(self):
        return get_object_or_404(models.TradingClaim, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

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


class RemoveUploadClaimView(UpdateView):
    model = models.TradingClaim
    form_class = forms.UploadClaimForm
    template_name = 'includes/claim.html'

    def get_object(self):
        return get_object_or_404(models.TradingClaim, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        self.object.filename = ''
        self.object.date_fulfilled = None
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.object.picture.name))
            os.remove(os.path.join(settings.MEDIA_ROOT, self.object.thumbnail_path))
        except OSError:
            pass
        self.object.picture = None
        return super(RemoveUploadClaimView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(RemoveUploadClaimView, self).get_context_data(*args, **kwargs)
        context['claim'] = self.object
        return context


class AcceptClaimView(UpdateView):
    model = models.TradingClaim
    form_class = forms.AcceptClaimForm
    template_name = 'includes/tradingtree_foryou.html'

    def get_object(self):
        return get_object_or_404(models.TradingClaim, pk=self.kwargs['claim_id'], user=self.request.user)

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

            self.object.offer.artist.num_characters = self.object.offer.artist.character_set.count()
            self.request.user.num_characters = self.request.user.character_set.count()

#                                Accepting this adoptable into your Characters section...

        return super(AcceptClaimView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(AcceptClaimView, self).get_context_data(*args, **kwargs)
        context['claim'] = self.object
        return context

    def get_success_url(self):
        return reverse('accept-claim', kwargs={'claim_id': self.object.id})


class ChooseAdopterView(UpdateView):
    model = models.TradingClaim
    form_class = forms.AcceptClaimForm

    def get_object(self):
        return get_object_or_404(models.TradingClaim, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        logger.info(self.object.date_fulfilled)
        if self.object.date_fulfilled:
            self.object.date_fulfilled = None
        else:
            self.object.date_fulfilled = timezone.now()
        return super(ChooseAdopterView, self).form_valid(form)


class RemoveClaimView(DeleteView):
    model = models.TradingClaim

    def get_object(self):
        return get_object_or_404(models.TradingClaim, (Q(user=self.request.user) | Q(offer__artist=self.request.user)), pk=self.kwargs['claim_id'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(self.object.picture.name)
        if self.object.offer.type == 'icon':
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, self.object.picture.name))
                os.remove(os.path.join(settings.MEDIA_ROOT, self.object.thumbnail))
            except OSError:
                pass
            return super(RemoveClaimView, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('offer', kwargs={'offer_id': self.object.offer.id})


class OfferView(DetailView):
    models = models.TradingOffer
    template_name = 'includes/offer.html'

    def get_object(self):
        return get_object_or_404(models.TradingOffer, pk=self.kwargs['offer_id'])


class EditOfferView(UpdateView):
    models = models.TradingOffer
    form_class = forms.OfferForm
    template_name = 'includes/edit_offer.html'

    def get_object(self):
        return get_object_or_404(models.TradingOffer, pk=self.kwargs['offer_id'], artist=self.request.user)


class OfferStatusView(APIView):

    def get(self, request, offer_id=None):
        response = {}
        offer = get_object_or_404(models.TradingOffer, pk=offer_id)
        for claim in offer.tradingclaim_set.all():
            if claim.picture:
                response[claim.id] = {
                    'thumbnail_url': claim.thumbnail_url,
                    'thumbnail_done': claim.thumbnail_created,
                }
        return Response(response)


class ColoringPicturesView(DetailView):
    models = models.ColoringBase
    template_name = 'includes/colored_pictures.html'

    def get_object(self):
        return get_object_or_404(models.ColoringBase, pk=self.kwargs['coloring_base_id'])

    def get_context_data(self, *args, **kwargs):
        context = super(ColoringPicturesView, self).get_context_data(*args, **kwargs)
        context['coloring_base'] = self.object
        return context


class UploadColoringPictureView(CreateView):
    model = models.ColoringPicture
    form_class = forms.UploadColoringPictureForm
    template_name = 'includes/colored_pictures.html'

#    def get_object(self):
#        return get_object_or_404(models.ColoringPic, pk=self.kwargs['claim_id'], offer__artist=self.request.user)

    def form_valid(self, form):
        response = {'success': False}

        coloring_base = get_object_or_404(models.ColoringBase, pk=self.kwargs['coloring_base_id'])

        coloring_picture = form.save(commit=False)
        coloring_picture.artist = self.request.user
        coloring_picture.base = coloring_base
        coloring_picture.save()

        coloring_picture.picture = self.request.FILES['picture']
        coloring_picture.filename = self.request.FILES['picture'].name
        coloring_picture.save()

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
        offer = get_object_or_404(models.ColoringBase, pk=coloring_base_id)
        for coloring_picture in offer.coloringpicture_set.all():
            if coloring_picture.picture and coloring_picture.filename:
                response[coloring_picture.id] = {
                    'thumbnail_url': coloring_picture.thumbnail_url,
                    'thumbnail_done': coloring_picture.thumbnail_created,
                }
        return Response(response)


class RemoveColoringPictureView(DeleteView):
    model = models.ColoringPicture

    def get_object(self):
        return get_object_or_404(models.ColoringPicture, (Q(artist=self.request.user) | Q(base__creator=self.request.user)), pk=self.kwargs['coloring_picture_id'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(self.object.picture.name)
        return super(RemoveColoringPictureView, self).delete(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('coloring-pictures', kwargs={'coloring_base_id': self.object.base.id})


class PicturePickerView(TemplateView):
    template_name = 'includes/pick_picture.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PicturePickerView, self).get_context_data(*args, **kwargs)

        folder_id = self.request.GET.get('folder_id', None)
        selected_folder = models.Folder.objects.filter(user=self.request.user, pk=folder_id).first()

        sort_by = self.request.GET.get('sort_by', None)
        if not sort_by in ['newest', 'oldest', 'popularity', 'comments']:
            sort_by = 'newest'

        context['folders'] = utils.tree_to_list(self.request.user.folder_set.all(), sort_by='name')
        pictures = self.request.user.picture_set.filter(date_deleted__isnull=True)

        if selected_folder:
            pictures = pictures.filter(folder=selected_folder)

        if sort_by == 'newest':
            pictures = pictures.order_by('-date_uploaded')
        elif sort_by == 'oldest':
            pictures = pictures.order_by('date_uploaded')
        elif sort_by == 'popularity':
            pictures = pictures.order_by('-num_faves')
        elif sort_by == 'comments':
            pictures = pictures.order_by('-num_comments')

        context['sort_by'] = sort_by
        context['selected_folder'] = selected_folder
        context['pictures'] = pictures

        return context


class PMsView(TemplateView):
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


class PMView(DetailView):
    model = models.PrivateMessage
    template_name = 'includes/pm.html'

    def get_object(self):
        return get_object_or_404(models.PrivateMessage, (Q(sender=self.request.user) | Q(recipient=self.request.user)), pk=self.kwargs['pm_id'])

    def get_context_data(self, *args, **kwargs):
        context = super(PMView, self).get_context_data(*args, **kwargs)

        if self.object.recipient == self.request.user and self.object.date_viewed == None:
            self.object.date_viewed = timezone.now()
            self.object.save()

        context['pm'] = self.object
        context['blocked'] = models.Block.objects.filter(user=context['pm'].sender, blocked_user=self.request.user).exists()

        return context


class PMCreateView(CreateView):
    model = models.PrivateMessage
    form_class = forms.PMForm

    def get_object(self):
        return get_object_or_404(models.PrivateMessage, (Q(sender=self.request.user) | Q(recipient=self.request.user)), pk=self.kwargs['pm_id'])

    def form_valid(self, form):
        pm = form.save(commit=False)
        pm.sender = self.request.user
        if pm.reply_to:
            pm.reply_to.date_replied = timezone.now()
            pm.reply_to.save()
            pm.subject = pm.reply_to.subject
            if not pm.subject.startswith('Re: '):
                pm.subject = 'Re: {0}'.format(pm.subject)
        pm.save()
        response = super(PMCreateView, self).form_valid(form)
        return response

#                <%
#                        String recptname = (String)pageContext.getAttribute("recptname");
#                        String recptemail = (String)pageContext.getAttribute("recptemail");
#                        String sendername = (String)pageContext.getAttribute("sendername");
#                        String msgBody = "This is an automated message from The Lion King Fan-Art Archive.\n\nYou have received a new Private Message from " + sendername + ".\n\nPlease visithttp://fanart.lionking.org and check your PMs in ArtManager.";
#                        sendEmail("fanart@lionking.org", recptemail, "TLKFAA Private Message", msgBody, false);
#                %>

    def get_success_url(self):
        return reverse('pm-success', kwargs={'pm_id': self.object.id})


class PMSuccessView(PMView):
    template_name = 'includes/pm_success.html'


class PMShoutView(TemplateView):
    template_name = 'includes/pm.html'

    def get_context_data(self, **kwargs):
        context = super(PMShoutView, self).get_context_data(**kwargs)

        context['shout'] = get_object_or_404(models.Shout, pk=self.kwargs['shout_id'], artist=self.request.user)
        context['recipient'] = context['shout'].user
        context['blocked'] = models.Block.objects.filter(user=context['recipient'], blocked_user=self.request.user).exists()

        return context


class PMUserView(TemplateView):
    template_name = 'includes/pm.html'

    def get_context_data(self, **kwargs):
        context = super(PMUserView, self).get_context_data(**kwargs)

        if 'recipient_id' in self.kwargs and self.kwargs['recipient_id']:
            context['recipient'] = get_object_or_404(models.User, pk=self.kwargs['recipient_id'])
            context['blocked'] = models.Block.objects.filter(user=context['recipient'], blocked_user=self.request.user).exists()

        return context


class PMsMoveView(APIView):

    def post(self, request, action):
        response = {'success': False, 'action': action, 'pm_ids': request.POST.get('pm_ids')}
        logger.info(action)
        for pm_id in (request.POST.get('pm_ids')).split(','):
            if not pm_id:
                continue
            try:
                pm = models.PrivateMessage.objects.get((Q(sender=self.request.user) | Q(recipient=self.request.user)), pk=pm_id)
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
            except models.PrivateMessage.DoesNotExist:
                logger.info('{0} not found'.format(pm_id))
                continue
        response['success'] = True
        return Response(response)


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


class CheckNameView(APIView):

    def get(self, request):
        artist_name = request.GET.get('name')
        dir_name = request.GET.get('dir_name')
        response = {
            'name_available': not models.User.objects.filter(Q(username=artist_name) | Q(dir_name=dir_name)).exists(),
        }
        return Response(response)


class SocialMediaIdentitiesView(TemplateView):
    template_name = 'includes/social_media.html'

    def get_context_data(self, **kwargs):
        context = super(SocialMediaIdentitiesView, self).get_context_data(**kwargs)

        context['social_medias'] = models.SocialMedia.objects.all()

        return context


class AddSocialMediaIdentityView(CreateView):
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


class RemoveSocialMediaIdentityView(DeleteView):
    model = models.SocialMediaIdentity

    def get_object(self):
        return get_object_or_404(models.SocialMediaIdentity, pk=self.kwargs['identity_id'], user=self.request.user)

    def get_success_url(self):
        return reverse('social-media-identities', kwargs={})


class UploadProfilePicView(UpdateView):
    model = models.User
    form_class = forms.UploadProfilePicForm

    def get_object(self):
        user = self.request.user
        self.old_profile_picture = user.profile_picture
        self.old_profile_pic_thumbnail_path = user.profile_pic_thumbnail_path
        return user

    def form_invalid(self, form):
        response = {'success': False}
        return JsonResponse(response)

    def form_valid(self, form):
        response = {'success': False}

        logger.info(self.request.FILES)
#        self.object.picture = self.request.FILES['picture']
#        self.object.filename = self.request.FILES['picture'].name
#        self.object.date_uploaded = timezone.now()

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

        return JsonResponse(response)

    def get_context_data(self, *args, **kwargs):
        context = super(UploadProfilePicView, self).get_context_data(*args, **kwargs)
        return context


class ProfilePicStatusView(APIView):

    def get(self, request, offer_id=None):
        response = {}
        if request.user.profile_picture:
            response = {
                'url': request.user.profile_pic_url,
                'thumbnail_url': request.user.profile_pic_thumbnail_url,
                'thumbnail_done': request.user.profile_pic_thumbnail_created,
            }
        return Response(response)


class RemoveProfilePicView(UpdateView):
    model = models.User
    form_class = forms.RemoveProfilePicForm

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = {'success': True}

        logger.info(self.object.profile_picture.name)
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.object.profile_picture.name))
            os.remove(self.object.profile_pic_thumbnail_path)
        except OSError:
            pass

        self.object.profile_picture = None
        self.object.profile_width = None
        self.object.profile_height = None
        self.object.save()

        return JsonResponse(response)
