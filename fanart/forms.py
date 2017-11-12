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


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        logger.warning(form.errors)
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            ajax_response = {
                'success': False,
                'errors': form.errors,
            }
#            return HttpResponse(form.errors.as_json())
            return HttpResponse(json.dumps(ajax_response))
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'success': True,
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class LoginForm(AuthenticationForm):

    def clean(self):
        m = hashlib.md5()
        username = self.cleaned_data.get('username')
        m.update(self.cleaned_data.get('password'))
        password = m.hexdigest()

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class PictureCommentForm(forms.ModelForm):
    comment = forms.CharField(label='Comment:')

    class Meta:
        model = models.PictureComment
        fields = ['user', 'picture', 'reply_to', 'comment', 'hash']


class PictureCommentUpdateForm(forms.ModelForm):
    comment = forms.CharField(label='Comment:')

    class Meta:
        model = models.PictureComment
        fields = ['comment']


class PictureCommentDeleteForm(forms.ModelForm):

    class Meta:
        model = models.PictureComment
        fields = []


class ShoutForm(forms.ModelForm):
    comment = forms.CharField(label='Comment:')

    class Meta:
        model = models.Shout
        fields = ['user', 'artist', 'comment']


class ClaimForm(forms.ModelForm):

    class Meta:
        model = models.TradingClaim
        fields = ['offer', 'comment', 'reference_url']


class OfferForm(forms.ModelForm):

    class Meta:
        model = models.TradingOffer
        fields = ['title', 'comment']


class UploadClaimForm(forms.ModelForm):

    class Meta:
        model = models.TradingClaim
        fields = ['picture']


class AcceptClaimForm(forms.ModelForm):

    class Meta:
        model = models.TradingClaim
        fields = []


class UploadColoringPictureForm(forms.ModelForm):

    class Meta:
        model = models.ColoringPicture
        fields = []


