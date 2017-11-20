from __future__ import unicode_literals

from django.shortcuts import render, render_to_response, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.utils import timezone
from django.shortcuts import render

from fanart import models
from fanart.views import UserPaneMixin


class BaseRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.session.get('am_page'):
            return reverse('artmanager:{0}'.format(self.request.session['am_page']))
        return reverse('artmanager:dashboard')


class ArtManagerPaneView(UserPaneMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super(ArtManagerPaneView, self).get_context_data(**kwargs)

        context['community_art_data'] = self.get_community_art_data()
        context['contests_data'] = self.get_contests_data()
        context['sketcher_users'] = range(12)

        return context


class DashboardView(ArtManagerPaneView):
    template_name = 'artmanager/dashboard.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'dashboard'
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return None

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        context['pms'] = self.request.user.pms_received.filter(date_viewed__isnull=True)
        context['box'] = 'in'

        return context


class PrefsView(DetailView):
#class ArtManagerPrefsView(DetailView, FormMixin):
    template_name = 'artmanager/prefs.html'
    model = models.User

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'prefs'
        return super(PrefsView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(PrefsView, self).get_context_data(**kwargs)

        context['social_medias'] = models.SocialMedia.objects.all()

        return context


class UploadView(TemplateView):
    template_name = 'artmanager/upload.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'upload'
        return super(UploadView, self).get(request, *args, **kwargs)


class ArtworkView(TemplateView):
    template_name = 'artmanager/artwork.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'artwork'
        return super(ArtworkView, self).get(request, *args, **kwargs)


class FoldersView(TemplateView):
    template_name = 'artmanager/folders.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'folders'
        return super(FoldersView, self).get(request, *args, **kwargs)


class ArtWallView(TemplateView):
    template_name = 'artmanager/artwall.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'artwall'
        return super(ArtWallView, self).get(request, *args, **kwargs)


class CharactersView(TemplateView):
    template_name = 'artmanager/characters.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'characters'
        return super(CharactersView, self).get(request, *args, **kwargs)


class CustomizeView(TemplateView):
    template_name = 'artmanager/customize.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'customize'
        return super(CustomizeView, self).get(request, *args, **kwargs)


class PrivateMessagesView(ArtManagerPaneView):
    template_name = 'artmanager/private_msgs.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'private-msgs'
        return super(PrivateMessagesView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PrivateMessagesView, self).get_context_data(**kwargs)

        context['pms'] = self.request.user.pms_received.all()
        context['box'] = 'in'

        return context


class TradingTreeView(TemplateView):
    template_name = 'artmanager/trading_tree.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'trading-tree'
        return super(TradingTreeView, self).get(request, *args, **kwargs)


class ColoringCaveView(TemplateView):
    template_name = 'artmanager/coloring_cave.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'coloring-cave'
        return super(ColoringCaveView, self).get(request, *args, **kwargs)


class ContestsView(TemplateView):
    template_name = 'artmanager/contests.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'contests'
        return super(ContestsView, self).get(request, *args, **kwargs)


class BulletinsView(TemplateView):
    template_name = 'artmanager/bulletins.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'artwork'
        return super(BulletinsView, self).get(request, *args, **kwargs)


class UploadHistoryView(TemplateView):
    template_name = 'artmanager/upload_history.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'upload-history'
        return super(UploadHistoryView, self).get(request, *args, **kwargs)


class CommentsView(TemplateView):
    template_name = 'artmanager/comments.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'comments'
        return super(CommentsView, self).get(request, *args, **kwargs)


class ShoutsView(TemplateView):
    template_name = 'artmanager/shouts.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'shouts'
        return super(ShoutsView, self).get(request, *args, **kwargs)


class FansView(TemplateView):
    template_name = 'artmanager/fans.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'fans'
        return super(FansView, self).get(request, *args, **kwargs)


class BlocksView(TemplateView):
    template_name = 'artmanager/blocks.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'blocks'
        return super(BlocksView, self).get(request, *args, **kwargs)
