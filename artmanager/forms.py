from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden

from fanart import models
from trading_tree.models import Offer, Claim
from coloring_cave.models import Base, ColoringPicture

import json
import hashlib

import logging
logger = logging.getLogger(__name__)


class PrefsForm(forms.ModelForm):
    email = forms.EmailField(error_messages={'required': 'You must enter a valid email address.'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={'required': 'You must enter a password.'})
    password_repeat = forms.CharField(widget=forms.PasswordInput, error_messages={'required': 'You must enter the password a second time.'})

    class Meta:
        model = models.User
        fields = ['description', 'is_public', 'show_email', 'birth_date', 'show_birthdate', 'show_birthdate_age',
            'gender', 'location', 'occupation', 'website',
            'allow_shouts', 'allow_comments', 'email_shouts', 'email_comments', 'email_pms',
            'show_coloring_cave', 'commissions_open', 'tooltips_enabled']


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
        fields = ['title', 'notes', 'keywords', 'allow_comments', 'work_in_progress', 'notify_on_approval', 'force_approve', 'reset_upload_date', 'replaces_picture', 'notify_fans_of_replacement']


class PendingForm(forms.ModelForm):

    class Meta:
        model = models.Pending
        fields = ['title', 'keywords']


class PictureForm(forms.ModelForm):

    class Meta:
        model = models.Picture
        fields = ['title', 'keywords', 'is_public', 'work_in_progress', 'allow_comments']


class ColoringPictureForm(forms.ModelForm):

    class Meta:
        model = ColoringPicture
        fields = ['comment']


class FolderForm(forms.ModelForm):

    class Meta:
        model = models.Folder
        fields = ['name', 'description']


class CharacterForm(forms.ModelForm):

    class Meta:
        model = models.Character
        fields = ['name', 'description', 'species', 'sex', 'story_title', 'story_url']


class CustomizeForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ['banner_text', 'banner_text_min']


class BannerPreviewForm(forms.Form):
    preview_text = forms.CharField()


class UploadIconOfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = ['title', 'comment']


class CreateAdoptableOfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = ['title', 'comment', 'character']


class PostColoringBaseForm(forms.ModelForm):

    class Meta:
        model = Base
        fields = []


class ContestForm(forms.ModelForm):

    class Meta:
        model = models.Contest
        fields = ['title', 'description', 'rules', 'date_end', 'allow_voting']


class ContestPublishForm(forms.ModelForm):

    class Meta:
        model = models.Contest
        fields = ['is_active']


class ContestCancelForm(forms.ModelForm):

    class Meta:
        model = models.Contest
        fields = ['is_active', 'is_cancelled']


class BulletinForm(forms.ModelForm):

    class Meta:
        model = models.Bulletin
        fields = ['title', 'bulletin']


class DeleteShoutForm(forms.ModelForm):

    class Meta:
        model = models.Shout
        fields = []


class DeleteCommentForm(forms.ModelForm):

    class Meta:
        model = models.PictureComment
        fields = []
