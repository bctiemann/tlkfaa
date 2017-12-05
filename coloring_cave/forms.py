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


class UploadColoringPictureForm(forms.ModelForm):

    class Meta:
        model = models.ColoringPicture
        fields = ['comment']

