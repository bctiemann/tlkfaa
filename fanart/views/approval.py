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
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin

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


class ApprovalView(UserPassesTestMixin, AccessMixin, TemplateView):
    template_name = 'approval/base.html'
    raise_exception = True

    def test_func(self):
        return self.request.user.is_approver

    def get_context_data(self, **kwargs):
        context = super(ApprovalView, self).get_context_data(**kwargs)

        context['pending_pictures'] = models.Pending.objects.filter(is_approved=False) \
            .exclude(Q(artist__auto_approve=True) \
                & ~(Q(force_approve=True) \
                | Q(width__gt=settings.APPROVAL_TRIGGER_WIDTH) \
                | Q(height__gt=settings.APPROVAL_TRIGGER_HEIGHT) \
                | Q(file_size__gt=settings.APPROVAL_TRIGGER_SIZE) \
                | Q(is_movie=True))) \
            .order_by('date_uploaded')[0:100]

#SELECT pending.*,artists.*,folders.name FROM artists,pending
#LEFT JOIN folders ON pending.folderid=folders.folderid
#WHERE pending.artistid=artists.artistid
#AND approved=false
#AND (autoapprove=false OR (
#(width>1200
#OR height>1200
#OR filesize>300000)
#AND ismovie=false)
#AND forceapprove=false
#)
#ORDER BY uploaded
#LIMIT ${approvepreload}
        context['threshold_width'] = settings.APPROVAL_WARNING_WIDTH
        context['threshold_height'] = settings.APPROVAL_WARNING_HEIGHT
        context['threshold_size'] = settings.APPROVAL_WARNING_SIZE

        return context

