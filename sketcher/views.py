# -*- coding: utf-8 -*-


from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
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


class SketcherWebLaunchView(LoginRequiredMixin, View):
    """
    Mints a short-lived, single-use Sketcher access token and redirects
    straight to the browser-based (sketcher-web) client with it embedded in
    the query string - the one-click path for users who should never need
    to touch the Java desktop client. Mirrors SketcherLaunchView's redirect-
    with-token pattern rather than SketcherLaunchApiView's fetch()-based
    JSON handoff, so no CORS or cross-origin cookie setup is required
    between this site and wherever sketcher-web ends up hosted - it is a
    plain ordinary redirect, and sketcher-web's own launch.ts already knows
    how to read token/server/port/nick straight off the URL.
    """
    def get(self, request):
        access_token = SketcherAccessToken.issue_for(request.user)
        query = urlencode({
            'token': access_token.token,
            'server': settings.SKETCHER_SERVER_HOST,
            'port': settings.SKETCHER_SERVER_WS_PORT,
            'nick': request.user.username,
        })
        return HttpResponseRedirect('{0}/?{1}'.format(settings.SKETCHER_WEB_URL, query))


class SketcherLaunchApiView(LoginRequiredMixin, View):
    """
    JSON sibling of SketcherLaunchView for the browser-based (WebSocket)
    client: same token minting, but returned as JSON for a same-origin
    fetch() caller instead of a sketcher:// redirect - there's no OS-level
    handoff needed when the client is itself a web page.
    """
    def get(self, request):
        access_token = SketcherAccessToken.issue_for(request.user)
        return JsonResponse({
            'token': access_token.token,
            'server': settings.SKETCHER_SERVER_HOST,
            'wsPort': settings.SKETCHER_SERVER_WS_PORT,
        })


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
