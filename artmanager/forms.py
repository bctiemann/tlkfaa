from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden

from fanart import models

import json
import hashlib

import logging
logger = logging.getLogger(__name__)


class PrefsForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ['description', 'email', 'is_public', 'show_email', 'birth_date', 'show_birthdate', 'show_birthdate_age',
            'gender', 'location', 'occupation', 'website',
            'allow_shouts', 'allow_comments', 'email_shouts', 'email_comments', 'email_pms',
            'show_coloring_cave', 'commissions_open',]


class ProfilePrefsForm(PrefsForm):

    class Meta:
        model = models.User
        fields = ['email', 'email_pms',]


class UserModeForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ['is_artist']
