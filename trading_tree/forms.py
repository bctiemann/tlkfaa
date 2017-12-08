from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden

from fanart import models
from trading_tree.models import Offer, Claim

import json
import hashlib

import logging
logger = logging.getLogger(__name__)


class ClaimForm(forms.ModelForm):

    class Meta:
        model = Claim
        fields = ['offer', 'comment', 'reference_url']


class OfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = ['title', 'comment']


class RemoveOfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = []


class UploadClaimForm(forms.ModelForm):

    class Meta:
        model = Claim
        fields = ['picture']

class AcceptClaimForm(forms.ModelForm):

    class Meta:
        model = Claim
        fields = []

