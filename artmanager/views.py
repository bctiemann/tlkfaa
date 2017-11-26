from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render, render_to_response, redirect, reverse, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash

from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models
from fanart import utils
from fanart.views import UserPaneMixin
from fanart.forms import AjaxableResponseMixin
from artmanager import forms

import json
import hashlib
import os
import shutil

import logging
logger = logging.getLogger(__name__)


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


class PrefsUpdateView(AjaxableResponseMixin, UpdateView):
    model = models.User
    form_class = forms.PrefsForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super(PrefsUpdateView, self).form_valid(form)

        logger.info(self.request.POST)

        user = form.save(commit=False)
        new_username = self.request.POST.get('username', None)
        if new_username and new_username != user.username:
            try:
                models.validate_unique_username(new_username)
            except ValidationError as e:
                ajax_response = {
                    'success': False,
                    'errors': {'username': e.messages},
                }
                return HttpResponse(json.dumps(ajax_response))

            user.username = new_username
            new_dir_name = user.change_dir_name()

            models.ArtistName.objects.create(artist=user, name=new_username)

        new_sort_name = self.request.POST.get('sort_name', None)
        if new_sort_name:
            user.sort_name = new_sort_name

        passwd = self.request.POST.get('passwd', None)
        passwd_repeat = self.request.POST.get('passwd_repeat', None)
        if passwd != '********':
            if passwd != passwd_repeat:
                ajax_response = {
                    'success': False,
                    'errors': {'password': ['The passwords you entered did not match']},
                }
                return HttpResponse(json.dumps(ajax_response))

            m = hashlib.md5()
            m.update(passwd)
            password_hash = m.hexdigest()
            user.set_password(password_hash)
            update_session_auth_hash(self.request, user)

        new_email = self.request.POST.get('email', None)
        if new_email != user.email:
            try:
                models.validate_unique_email(new_email)
            except ValidationError as e:
                ajax_response = {
                    'success': False,
                    'errors': {'username': e.messages},
                }
                return HttpResponse(json.dumps(ajax_response))

            user.email = new_email

        user.save()

        return response


class PrefsUpdateProfileView(PrefsUpdateView):
    form_class = forms.ProfilePrefsForm


class UserModeView(AjaxableResponseMixin, UpdateView):
    model = models.User
    form_class = forms.UserModeForm

    def get_object(self, queryset=None):
        return self.request.user


class UploadView(TemplateView):
    template_name = 'artmanager/upload.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'upload'
        return super(UploadView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        replacing_picture = None
        replacing_picture_id = self.request.GET.get('replace', None)
        logger.info(replacing_picture_id)
        if replacing_picture_id:
            try:
                replacing_picture = models.Picture.objects.get(pk=replacing_picture_id, artist=self.request.user)
                context['tagged_characters'] = [pc.character for pc in replacing_picture.picturecharacter_set.all()]
                context['tag_list'] = ','.join([str(character.id) for character in context['tagged_characters']])
            except models.Picture.DoesNotExist:
                pass

        context['replacing_picture'] = replacing_picture
        context['max_title_chars'] = settings.MAX_PICTURE_TITLE_CHARS
        context['canon_characters'] = models.Character.objects.filter(is_canon=True).order_by('name')

        return context


class UploadFormView(TemplateView):
    template_name = 'artmanager/upload_form.html'


class UploadFileView(CreateView):
    model = models.Pending
    form_class = forms.UploadFileForm
#    template_name = 'includes/colored_pictures.html'

    def form_valid(self, form):
        response = {'success': False}

        logger.info(self.request.POST)

        try:
            folder = models.Folder.objects.get(pk=self.request.POST.get('folder', None), user=self.request.user)
        except models.Folder.DoesNotExist:
            folder = None

        pending = form.save(commit=False)
        pending.artist = self.request.user
        pending.folder = folder
        pending.picture = self.request.FILES['picture']
        pending.filename = self.request.FILES['picture'].name
        pending.save(update_thumbs=False)

        for character_id in (self.request.POST.get('characters')).split(','):
            if character_id:
                logger.info(character_id)
                try:
                    character = models.Character.objects.get(pk=character_id)
                except models.Character.DoesNotExist:
                    continue
                logger.info(character)
                pc = models.PictureCharacter.objects.create(pending=pending, character=character)
                logger.info(pc)

        super(UploadFileView, self).form_valid(form)

        response['success'] = True
        response['pending_id'] = pending.id

        return JsonResponse(response)

    def get_context_data(self, *args, **kwargs):
        context = super(UploadFileView, self).get_context_data(*args, **kwargs)
        return context


class UploadSuccessView(DetailView):
    template_name = 'artmanager/upload_success.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'], artist=self.request.user)


class PendingStatusView(APIView):

    def get(self, request, pending_id=None):
        response = {}
        for pending in request.user.pending_set.all():
            response[pending.id] = {
                'thumbnail_url': pending.thumbnail_url,
                'thumbnail_done': pending.thumbnail_created,
            }
        return Response(response)


class PendingView(TemplateView):
    template_name = 'artmanager/pending.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'pending'
        return super(PendingView, self).get(request, *args, **kwargs)


class PendingDetailView(DetailView):
    template_name = 'includes/pending.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'], artist=self.request.user)


class PendingFormView(DetailView):
    model = models.Pending
    template_name = 'artmanager/edit_pending.html'

    def get_object(self):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'], artist=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(PendingFormView, self).get_context_data(**kwargs)

        context['folders'] = utils.tree_to_list(self.request.user.folder_set.all(), sort_by='name')
        context['canon_characters'] = models.Character.objects.filter(is_canon=True).order_by('name')
        context['tag_list'] = ','.join([str(character.id) for character in self.object.tagged_characters])

        return context

class PendingUpdateView(UpdateView):
    model = models.Pending
    form_class = forms.PendingForm
    template_name = 'artmanager/edit_pending.html'

    def get_object(self):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'], artist=self.request.user)

    def form_valid(self, form):
        response = super(PendingUpdateView, self).form_valid(form)

        logger.info(self.request.POST)

        self.object.picturecharacter_set.all().delete()
        for character_id in (self.request.POST.get('characters')).split(','):
            if character_id:
                logger.info(character_id)
                try:
                    character = models.Character.objects.get(pk=character_id)
                except models.Character.DoesNotExist:
                    continue
                logger.info(character)
                pc = models.PictureCharacter.objects.create(pending=self.object, character=character)

        return response

class PendingDeleteView(DeleteView):
    model = models.Pending

    def get_object(self):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'], artist=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = {'success': False}

        self.object = self.get_object()

        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'pending', self.object.directory), ignore_errors=True)

        self.object.delete()

        response['success'] = True

        return JsonResponse(response)


class ArtworkView(TemplateView):
    template_name = 'artmanager/artwork.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'artwork'
        return super(ArtworkView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ArtworkView, self).get_context_data(**kwargs)

        folder = None
        folder_id = self.request.GET.get('folderid', None)
        if folder_id:
            try:
                folder = models.Folder.objects.get(pk=folder_id, user=self.request.user)
            except models.Folder.DoesNotExist:
                pass

        pictures = self.request.user.picture_set.filter(folder=folder)

        context['folder'] = folder
        context['pictures'] = pictures

        return context

class PictureDetailView(DetailView):
    template_name = 'artmanager/picture_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Picture, pk=self.kwargs['picture_id'], artist=self.request.user)


class PictureFormView(DetailView):
    template_name = 'artmanager/picture_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Picture, pk=self.kwargs['picture_id'], artist=self.request.user)


class TagCharactersView(TemplateView):
    template_name = 'artmanager/tag_characters.html'

    def get(self, request, *args, **kwargs):
        return super(TagCharactersView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TagCharactersView, self).get_context_data(**kwargs)

        tag_list = self.request.GET.get('taglist', None)
        if tag_list:
            context['tag_list'] = tag_list
            context['tagged_characters'] = models.Character.objects.filter(pk__in=tag_list.split(','))

        context['canon_characters'] = models.Character.objects.filter(is_canon=True).order_by('name')

        return context


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

