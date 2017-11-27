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
    email = forms.EmailField()

    class Meta:
        model = models.User
        fields = ['description', 'is_public', 'show_email', 'birth_date', 'show_birthdate', 'show_birthdate_age',
            'gender', 'location', 'occupation', 'website',
            'allow_shouts', 'allow_comments', 'email_shouts', 'email_comments', 'email_pms',
            'show_coloring_cave', 'commissions_open',]


class ProfilePrefsForm(PrefsForm):

    class Meta:
        model = models.User
        fields = ['email_pms',]


class UserModeForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ['is_artist']


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = models.Pending
        fields = ['title', 'notes', 'keywords', 'allow_comments', 'work_in_progress', 'notify_approval', 'force_approve', 'reset_upload_date', 'replaces_picture']


class PendingForm(forms.ModelForm):

    class Meta:
        model = models.Pending
        fields = ['title', 'keywords', 'folder']


class PictureForm(forms.ModelForm):

    class Meta:
        model = models.Picture
        fields = ['title', 'keywords', 'is_public', 'work_in_progress', 'allow_comments']


class ColoringPictureForm(forms.ModelForm):

    class Meta:
        model = models.ColoringPicture
        fields = ['comment']
