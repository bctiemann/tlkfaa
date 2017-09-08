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

from fanart.models import User


class ArtManagerRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.session.get('am_page'):
            return reverse('artmanager:{0}'.format(self.request.session['am_page']))
        return reverse('artmanager:dashboard')


class ArtManagerDashboardView(TemplateView):
    template_name = 'fanart/special.html'

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'dashboard'
        return super(ArtManagerDashboardView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return None


class ArtManagerPrefsView(DetailView):
#class ArtManagerPrefsView(DetailView, FormMixin):
    template_name = 'fanart/special.html'
    model = User

    def get(self, request, *args, **kwargs):
        request.session['am_page'] = 'prefs'
        return super(ArtManagerPrefsView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user
