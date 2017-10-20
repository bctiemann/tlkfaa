from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden

from fanart import models

import json

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

