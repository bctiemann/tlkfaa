# -*- coding: utf-8 -*-


from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View

from rest_framework.views import APIView
from rest_framework.response import Response

from sketcher.models import SketcherAccessToken, Ban


class SketcherLaunchRedirect(HttpResponseRedirect):
    """
    HttpResponseRedirect validates the target's scheme against an allowlist
    (http/https/ftp) as an open-redirect protection, and rejects anything
    else with a 400 - which includes sketcher://. Explicitly allow it here
    rather than relaxing the check globally.
    """
    allowed_schemes = HttpResponseRedirect.allowed_schemes + ['sketcher']


class SketcherLaunchView(LoginRequiredMixin, View):
    """
    Mints a short-lived, single-use Sketcher access token for the logged-in
    user and redirects straight to sketcher://launch?... - no intermediate
    page. The browser hands the redirect off to the OS, which launches (or
    focuses) the registered Sketcher client. If the client isn't installed/
    registered, the browser's own native handling for an unrecognized
    scheme takes over (there's no page here to show custom fallback
    instructions on).
    """
    def get(self, request):
        access_token = SketcherAccessToken.issue_for(request.user)
        query = urlencode({
            'token': access_token.token,
            'server': settings.SKETCHER_SERVER_HOST,
            'port': settings.SKETCHER_SERVER_PORT,
        })
        return SketcherLaunchRedirect('sketcher://launch?{0}'.format(query))


class SketcherVerifyTokenView(APIView):
    """
    Machine-to-machine endpoint called by the Sketcher (Java) server to
    redeem an access token minted by SketcherLaunchView. Authenticated by
    a shared API key (SKETCHER_API_KEY), not by Django session/user auth -
    the caller is the Sketcher server, not a logged-in browser.
    """
    permission_classes = ()

    def post(self, request):
        api_key = request.headers.get('X-Sketcher-Api-Key')
        if not settings.SKETCHER_API_KEY or api_key != settings.SKETCHER_API_KEY:
            return Response({'valid': False, 'detail': 'Invalid API key.'}, status=403)

        token_value = request.data.get('token')
        if not token_value:
            return Response({'valid': False, 'detail': 'No token provided.'})

        try:
            access_token = SketcherAccessToken.objects.select_related('user').get(token=token_value)
        except SketcherAccessToken.DoesNotExist:
            return Response({'valid': False, 'detail': 'Unknown token.'})

        if not access_token.is_valid():
            return Response({'valid': False, 'detail': 'Token has expired or already been used.'})

        if Ban.objects.filter(user=access_token.user).exists():
            return Response({'valid': False, 'detail': 'This user is banned from Sketcher.'})

        access_token.mark_used()

        return Response({'valid': True, 'username': access_token.user.username})
