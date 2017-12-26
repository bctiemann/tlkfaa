from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import capfirst
from django.utils.translation import ugettext, ugettext_lazy as _

from fanart import models

import json
import hashlib

import logging
logger = logging.getLogger(__name__)

UserModel = get_user_model()


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
        logger.info(self.cleaned_data)
        username = self.cleaned_data.get('username')
        raw_password = self.cleaned_data.get('password')

        if username is not None and raw_password:
            m.update(raw_password)
            password = m.hexdigest()
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


class VisibleFaveForm(forms.ModelForm):

    class Meta:
        model = models.Favorite
        fields = ['is_visible']


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


class ContestEntryForm(forms.ModelForm):

    class Meta:
        model = models.ContestEntry
        fields = []


class ContestVoteForm(forms.ModelForm):

    class Meta:
        model = models.ContestVote
        fields = ['entry']


#class PMForm(forms.ModelForm):

#    class Meta:
#        model = models.PrivateMessage
#        fields = ['reply_to', 'subject', 'message', 'recipient']


class SocialMediaIdentityForm(forms.ModelForm):

    class Meta:
        model = models.SocialMediaIdentity
        fields = ['social_media', 'identity']


class UploadProfilePicForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = ['profile_picture']


class RemoveProfilePicForm(forms.ModelForm):

    class Meta:
        model = models.User
        fields = []


class UploadBannerForm(forms.ModelForm):

    class Meta:
        model = models.Banner
        fields = ['picture']


class GiftPictureForm(forms.ModelForm):

    class Meta:
        model = models.GiftPicture
        fields = ['reply_message']


class ApprovalForm(forms.ModelForm):

    class Meta:
        model = models.Pending
        fields = []


class RegisterForm(forms.Form):
    username = forms.CharField(validators=[models.validate_unique_username], error_messages={'required': 'You must enter a profile name.'})
    email = forms.EmailField(validators=[models.validate_unique_email], error_messages={'required': 'You must enter a valid email address.'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={'required': 'You must enter a password.'})
    password_repeat = forms.CharField(widget=forms.PasswordInput, error_messages={'required': 'You must enter the password a second time.'})
    is_artist = forms.BooleanField(required=False)


class RecoverUsernameForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254, required=False)


class UsernameAwarePasswordResetForm(PasswordResetForm):
    username = forms.CharField(label=_("Username"), max_length=254, required=False)
    email = forms.EmailField(label=_("Email"), max_length=254, required=False)

    def get_users(self, email=None, username=None):
        """Given an email or username, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users_by_email = UserModel._default_manager.filter(**{
            '%s__iexact' % UserModel.get_email_field_name(): email,
            'is_active': True,
        })
        active_users_by_username = UserModel._default_manager.filter(**{
            'username__iexact': username,
            'is_active': True,
        })
        users = []
        for u in active_users_by_email:
            if u.has_usable_password() and u.email:
                users.append(u)
        for u in active_users_by_username:
            if u.has_usable_password() and u.email:
                users.append(u)
        logger.info(users)
        return list(set(users))

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        logger.info(self.cleaned_data)
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        logger.info(username, email)
        for user in self.get_users(email=email, username=username):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            logger.info(user.email)
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user.email, html_email_template_name=html_email_template_name,
            )


class HashedSetPasswordForm(SetPasswordForm):

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]

        m = hashlib.md5()
        m.update(password)
        password_hash = m.hexdigest()
        self.user.set_password(password_hash)

        if commit:
            self.user.save()
        return self.user

