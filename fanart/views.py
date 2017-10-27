from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models, forms, utils

from datetime import timedelta
import uuid
import json

import logging
logger = logging.getLogger(__name__)


class LoginView(LoginView):
    form_class = forms.LoginForm


class UserPaneView(TemplateView):

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

    def get_context_data(self, **kwargs):
        context = super(UserPaneView, self).get_context_data(**kwargs)
        context['sketcher_users'] = range(12)

        return context


class HomeView(UserPaneView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['current_contest'] = models.Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()
        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['admin_announcements'] = [models.Bulletin.objects.filter(is_published=True, is_admin=True).order_by('-date_posted').first()]
        context['bulletins'] = models.Bulletin.objects.filter(is_published=True, is_admin=False).order_by('-date_posted')[0:5]
        context['recently_active_artists'] = models.User.objects.recently_active()
        return context


class ArtistsView(UserPaneView):
    template_name = 'fanart/artists.html'


class ArtworkView(UserPaneView):
    template_name = 'fanart/artwork.html'


class CharactersView(UserPaneView):
    template_name = 'fanart/characters.html'


class TradingTreeView(UserPaneView):
    template_name = 'fanart/tradingtree.html'


class ColoringCaveView(UserPaneView):
    template_name = 'fanart/coloringcave.html'


class SpecialFeaturesView(UserPaneView):
    template_name = 'fanart/special.html'


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
        logger.info(artist)
        context['artist'] = artist
        context['shouts'] = artist.shouts_received.order_by('-date_posted')
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
        shout = form.save(commit=False)
        shout.user = self.request.user
        logger.info(shout.user)
        shout.save()
        response = super(PostShoutView, self).form_valid(form)
        return response


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
        context['picture_is_private'] = not picture.is_public and (not user.is_authenticated or picture.artist != user)
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

        context['last_nine_uploads'] = artist.picture_set.filter(is_public=True, date_deleted__isnull=True).order_by('-date_uploaded')[0:9]
        context['nine_most_popular_pictures'] = artist.picture_set.filter(num_faves__gt=0, is_public=True, date_deleted__isnull=True).order_by('-num_faves')[0:9]
        context['last_nine_coloring_pictures'] = artist.coloringpicture_set.filter(base__is_visible=True).order_by('-date_posted')[0:9]

        if self.request.user.is_authenticated():
            context['fave_artist'] = models.Favorite.objects.filter(artist=artist, user=self.request.user).first()

        return context
