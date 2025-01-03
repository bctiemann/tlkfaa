from PIL import UnidentifiedImageError

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.template import loader
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView, FormMixin
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, OuterRef, Subquery, Min, Max, Count
from django.db import connection
from django.forms import ValidationError
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from fanart import models, forms, tasks
from fanart import views as fanart_views
from fanart.forms import AjaxableResponseMixin

from fanart.response import JSONResponse, response_mimetype
from fanart.serialize import serialize

from datetime import timedelta
import uuid
import json
import random
import mimetypes
import os
from PIL import Image

import logging
logger = logging.getLogger(__name__)


class ApprovalAPIView(UserPassesTestMixin, AccessMixin, APIView):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_approver


class ApprovalUpdateView(UserPassesTestMixin, AccessMixin, UpdateView):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_approver


class ApprovalCreateView(UserPassesTestMixin, AccessMixin, CreateView):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_approver


class ApprovalTemplateView(UserPassesTestMixin, AccessMixin, TemplateView):
    raise_exception = True

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_approver

    def handle_no_permission(self):
        template = loader.get_template('403.html')
        return HttpResponseForbidden(
            template.render(request=self.request)
        )

class ApprovalHomeView(ApprovalTemplateView):
    template_name = 'approval/base.html'

    def get_context_data(self, **kwargs):
        context = super(ApprovalHomeView, self).get_context_data(**kwargs)
        context['pending_pictures'] = models.Pending.objects.requiring_approval().filter(picture__isnull=False)[0:100]
        context['threshold_width'] = settings.APPROVAL_WARNING_WIDTH
        context['threshold_height'] = settings.APPROVAL_WARNING_HEIGHT
        context['threshold_size'] = settings.APPROVAL_WARNING_SIZE
        return context


class PendingDetailView(ApprovalTemplateView):
    template_name = 'approval/pending.html'

    def get_context_data(self, **kwargs):
        context = super(PendingDetailView, self).get_context_data(**kwargs)
        context['pending'] = get_object_or_404(models.Pending, pk=self.kwargs['pending_id'])
        context['threshold_width'] = settings.APPROVAL_WARNING_WIDTH
        context['threshold_height'] = settings.APPROVAL_WARNING_HEIGHT
        context['threshold_size'] = settings.APPROVAL_WARNING_SIZE
        return context

class PendingListView(ApprovalHomeView):
    template_name = 'approval/pending_list.html'


class PendingCountView(ApprovalAPIView):

    def get(self, request):
        response = {'count': models.Pending.objects.requiring_approval().exclude(failed_processing=True).count()}
        return Response(response)


class PendingApproveView(ApprovalAPIView):

    def post(self, request, pending_id):
        response = {'success': True}
        pending = get_object_or_404(models.Pending, pk=pending_id)
        logger.info(f'{request.user} approved pending {pending}')

        pending.filename = '{0}.{1}'.format(request.POST.get('filename'), pending.extension)
        pending.is_approved = True
        pending.approved_by = request.user
        pending.save()

#        new_comments = request.POST.get('newcomments')
#        if new_comments:
#            pending.artist.comments += '{0}\n\n{1}'.format(timezone.now().strftime('%Y-%m-%d'), new_comments)
#            pending.artist.save()

        send_email = False
        subject = None
        text_template = None
        html_template = None
        if request.POST.get('warn_ot'):
            logger.info('Off-topic warning')
            subject = 'Fan Art Submission (off-topic warning)'
            text_template = 'email/approval/warning_offtopic.txt'
            html_template = 'email/approval/warning_offtopic.html'
            send_email = True

        if request.POST.get('warn_copied'):
            logger.info('Originality warning')
            subject = 'Fan Art Submission (originality warning)'
            text_template = 'email/approval/warning_originality.txt'
            html_template = 'email/approval/warning_originality.html'
            send_email = True

        if send_email:
            tasks.send_pending_moderation_email.delay(pending.id, subject, text_template, html_template)

        logger.info(request.POST)
        return Response(response)


class PendingRejectView(ApprovalAPIView):

    def post(self, request, pending_id):
        response = {'success': True}
        pending = get_object_or_404(models.Pending, pk=pending_id)
        logger.info(f'{request.user} rejected pending {pending}')

        send_email = False
        subject = None
        text_template = None
        html_template = None
        if request.POST.get('reason') == 'copied':
            logger.info('Copied')
            subject = 'Fan Art Submission (unable to accept)'
            text_template = 'email/approval/rejected_copied.txt'
            html_template = 'email/approval/rejected_copied.html'
            send_email = True
        elif request.POST.get('reason') == 'off-topic':
            logger.info('Off-topic')
            subject = 'Fan Art Submission (unable to accept)'
            text_template = 'email/approval/rejected_offtopic.txt'
            html_template = 'email/approval/rejected_offtopic.html'
            send_email = True
        elif request.POST.get('reason') == 'inappropriate':
            logger.info('Inappropriate')
            subject = 'Fan Art Submission (unable to accept)'
            text_template = 'email/approval/rejected_inappropriate.txt'
            html_template = 'email/approval/rejected_inappropriate.html'
            send_email = True
        elif request.POST.get('reason') == 'reupload':
            logger.info('Requested re-upload')
            subject = 'Fan Art Submission (please re-upload {0})'.format(pending.filename)
            text_template = 'email/approval/rejected_reupload.txt'
            html_template = 'email/approval/rejected_reupload.html'
            send_email = True
        else:
            logger.info('Silently deleted')

        if send_email:
            attachments = []
            with open(pending.picture.path, 'rb') as file:
                image_data = file.read()
            attachments.append({'filename': pending.picture.name, 'content': image_data, 'mimetype': pending.mime_type})

            tasks.send_pending_moderation_email.delay(
                pending.id, subject, text_template, html_template, attachments=attachments
            )

        pending.delete()

        logger.info(request.POST)
        return Response(response)


class PendingResizeView(ApprovalUpdateView):
    template_name = 'approval/pending.html'
    form_class = forms.ApprovalForm

    def get_object(self):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'])

    def form_valid(self, form):

        try:
            width = int(self.request.POST.get('width'))
        except ValueError:
            width = None
        try:
            height = int(self.request.POST.get('height'))
        except ValueError:
            height = None
        try:
            quality = int(self.request.POST.get('quality'))
        except ValueError:
            quality = 90

        im = Image.open(self.object.picture.path)
        orig_width = im.width
        orig_height = im.height

        if height:
            im = im.resize((int(orig_width * height / orig_height), height), Image.ANTIALIAS)
        elif width:
            im = im.resize((width, int(orig_height * width / orig_width)), Image.ANTIALIAS)

        im.save(self.object.picture.path, im.format, quality=quality)
        self.object.width = im.width
        self.object.height = im.height
        self.object.save(update_thumbs=False)

        logger.info(f'{self.request.user} resized pending {self.object}')
        logger.info(self.request.POST)

        return super(PendingResizeView, self).form_valid(form)

    def get_success_url(self):
        return reverse('pending-detail', kwargs={'pending_id': self.object.id})


class PendingConvertView(ApprovalUpdateView):
    template_name = 'approval/pending.html'
    form_class = forms.ApprovalForm

    def get_object(self):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'])

    def form_valid(self, form):
        im = Image.open(self.object.picture.path)
        image_dir = os.path.dirname(os.path.realpath(self.object.picture.path))
        rgb_im = im.convert('RGB')
        rgb_im.save('{0}/{1}.jpg'.format(image_dir, self.object.sanitized_basename))
        os.remove(os.path.realpath(self.object.picture.path))
        self.object.filename = '{0}.jpg'.format(self.object.sanitized_basename)
        new_picture_path = self.object.picture.name.split('/')[0:-1]
        new_picture_path.append('{0}.jpg'.format(self.object.sanitized_basename))
        self.object.picture = '/'.join(new_picture_path)

        logger.info(self.request.POST)

        return super(PendingConvertView, self).form_valid(form)

    def get_success_url(self):
        return reverse('pending-detail', kwargs={'pending_id': self.object.id})


class PendingUploadThumbView(ApprovalUpdateView):
    model = models.Pending
    form_class = forms.ApprovalForm
    template_name = 'approval/pending.html'

    def get_object(self):
        return get_object_or_404(models.Pending, pk=self.kwargs['pending_id'])

    def form_valid(self, form):
        response = {'success': False}

        max_pixels = settings.THUMB_SIZE['small']
        try:
            im_thumb = Image.open(self.request.FILES['picture'])
        except UnidentifiedImageError:
            response['message'] = 'Uploaded image failed processing.'
            return JsonResponse(response)

        orig_height = im_thumb.height
        orig_width = im_thumb.width
        logger.info(im_thumb)
        im_thumb.thumbnail((max_pixels, max_pixels * orig_height / orig_width))
        im_thumb.save(self.object.thumbnail_path, im_thumb.format)

        max_pixels = settings.THUMB_SIZE['large']
        im_preview = Image.open(self.request.FILES['picture'])
        orig_height = im_preview.height
        orig_width = im_preview.width
        logger.info(im_preview)
        im_preview.thumbnail((max_pixels, max_pixels * orig_height / orig_width))
        im_preview.save(self.object.preview_path, im_preview.format)

#        self.object.picture = self.request.FILES['picture']
#        self.object.filename = self.request.FILES['picture'].name
#        self.object.date_uploaded = timezone.now()
#        super(UploadClaimView, self).form_valid(form)

        self.object.has_thumb = True
        self.object.failed_processing = False
        if not self.object.width or self.object.height:
            self.object.width = orig_width
            self.object.height = orig_height
        self.object.save()
        response['success'] = True

        return JsonResponse(response)

    def get_context_data(self, *args, **kwargs):
        context = super(PendingUploadThumbView, self).get_context_data(*args, **kwargs)
        context['pending'] = self.object
        return context


#class PendingThumbStatusView(APIView):
#
#    def get(self, request, offer_id=None):
#        response = {}
#        if request.user.profile_picture:
#            response = {
#                'url': request.user.profile_pic_url,
#                'thumbnail_url': request.user.profile_pic_thumbnail_url,
#                'thumbnail_done': request.user.profile_pic_thumbnail_created,
#            }
#        return Response(response)


class AutoApprovalView(AjaxableResponseMixin, ApprovalUpdateView):
    model = models.User
    form_class = forms.AutoApprovalForm
    template_name = 'approval/pending.html'

    def get_object(self):
        return get_object_or_404(models.User, pk=self.kwargs['artist_id'])

    def form_valid(self, form):
        message = '{0} granted auto-approval to {1}'.format(self.request.user.username, self.object)
        logger.info(message)

        email_context = {'message': message}
        subject = 'TLKFAA: Auto-approval granted to {0}'.format(self.object.username)
        tasks.send_email.delay(
            recipients=[settings.ADMIN_EMAIL],
            subject=subject,
            context=email_context,
        )
        return super(AutoApprovalView, self).form_valid(form)


class ModNotesView(ApprovalTemplateView):
    template_name = 'approval/mod_notes.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(ModNotesView, self).get_context_data(*args, **kwargs)
        context['artist'] = get_object_or_404(models.User, pk=self.kwargs['artist_id'])
        return context


class AddModNoteView(ApprovalCreateView):
    model = models.ModNote
    form_class = forms.ModNoteForm
    template_name = 'approval/mod_notes.html'
    
    def form_valid(self, form):
        artist = get_object_or_404(models.User, pk=self.kwargs['artist_id'])
        logger.info(self.request.POST)
        mod_note = form.save(commit=False)
        mod_note.artist = artist
        mod_note.moderator = self.request.user
        mod_note.save()
        return super(AddModNoteView, self).form_valid(form)

    def get_success_url(self):
        return reverse('pending-mod-notes', kwargs={'artist_id': self.object.artist.id})


class PendingThumbStatusView(APIView):

    def get(self, request, pending_id=None):
        response = {}
        try:
            for pending in models.Pending.objects.all():
                response[pending.id] = {
                    'thumbnail_url': pending.thumbnail_url,
                    'preview_url': pending.preview_url,
                    'thumbnail_done': pending.thumbnail_created,
                    'preview_done': pending.preview_created,
                }
        except FileNotFoundError:
            pass
        return Response(response)

