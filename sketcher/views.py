# -*- coding: utf-8 -*-


import logging
import os
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response

from sketcher.models import SketcherAccessToken, Ban

logger = logging.getLogger(__name__)


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


# --- Sketcher admin page --------------------------------------------------
#
# Ported from the pre-2017 JSP admin (Sketcher/admin.jsp,
# ajax_sketcheradmin.jsp, ajax_sketcherlog.jsp, ajax_resetstatus.jsp,
# resetwarn.pl) onto the same two files sketcher-server already exposes -
# talk.txt (a one-way command queue its own background thread polls every
# second: ServerContext.java) and user.txt (the live roster, already read
# by UserPaneMixin.get_sketcher_user_names for the userpane box) - rather
# than adding any new API surface to the Java server itself.
#
# Not ported: the old sketcheradmins/sketcheradminvotes peer-nomination
# system for *becoming* an admin (superseded here by is_sketcher_mod,
# set directly via the Django admin) and the private admin-only "blog"
# (adminblog table) - a notes board with no functional tie to Sketcher
# itself.

def _read_sketcher_user_names():
    # Same logic as UserPaneMixin.get_sketcher_user_names (fanart/views) -
    # duplicated rather than imported to keep this admin-only module from
    # depending on fanart's view layer for what is, on both sides, a
    # trivial file read.
    if not settings.SKETCHER_USER_FILE_PATH:
        return []
    try:
        with open(settings.SKETCHER_USER_FILE_PATH) as f:
            return [line.strip() for line in f if line.strip()]
    except OSError:
        return []


def _make_group_writable(path):
    # talk.txt (and SKETCHER_RESET_KEY_PATH below) is written by this
    # process - running as the web server's own user - but has to be
    # read *and truncated* by sketcher-server, which runs as a different
    # user entirely. If whichever side creates the file first leaves it
    # at a plain default-umask 644, the other side can read it but not
    # write it - which is exactly what happened in production: talk.txt
    # ended up owner=www (this process), group=sketcher, mode 644, so
    # sketcher-server's own truncate-after-read (ServerContext.java, in
    # its talk.txt poller's finally block) hit a permission error on
    # every single 1-second poll - and that specific catch block swallows
    # the IOException with no log line at all, so the failure was
    # completely invisible until a broadcast kept re-appearing every
    # second until someone manually emptied the file. This can only fix
    # a file this process itself owns (chmod requires ownership, not just
    # write access) - logged rather than raised if it fails, since a
    # permission problem here shouldn't take down the request that
    # triggered it.
    try:
        os.chmod(path, 0o664)
    except OSError as e:
        logger.warning('Could not chmod %s to be group-writable: %s', path, e)


def _write_sketcher_talk_line(line):
    # Append-only - sketcher-server's own poller drains and truncates this
    # file itself once a second (ServerContext.java), so this only ever
    # needs to add its line to the end, matching the old JSP's own
    # FileWriter(path, true) (append mode).
    if not settings.SKETCHER_TALK_FILE_PATH:
        return
    with open(settings.SKETCHER_TALK_FILE_PATH, 'a') as f:
        f.write(line + '\n')
    _make_group_writable(settings.SKETCHER_TALK_FILE_PATH)


def _tail_sketcher_log():
    # Reads the whole file rather than shelling out to `tail` (what the
    # old JSP did via Runtime.exec) - simpler and avoids a subprocess, at
    # the cost of not scaling to a huge log file. Fine for a log this rc.d
    # service alone writes to; revisit if that ever stops being true.
    if not settings.SKETCHER_LOG_FILE_PATH:
        return []
    try:
        with open(settings.SKETCHER_LOG_FILE_PATH) as f:
            lines = f.readlines()
    except OSError:
        return []
    return [line.rstrip('\n') for line in lines[-settings.SKETCHER_LOG_TAIL_LINES:]]


def _sketcher_reset_cancelled():
    if not settings.SKETCHER_RESET_KEY_PATH:
        return False
    return os.path.exists(settings.SKETCHER_RESET_KEY_PATH)


def _sketcher_reset_status_context():
    # Shared by SketcherAdminView's initial render and
    # SketcherAdminResetStatusView's polling refresh, so the two can't
    # drift out of sync with each other about what "next reset" means.
    next_reset = _get_sketcher_next_reset()
    mins = int((next_reset - timezone.now()).total_seconds() // 60) if next_reset else None
    return {
        'sketcher_next_reset': next_reset,
        'sketcher_reset_mins': mins,
        'sketcher_reset_cancelled': _sketcher_reset_cancelled(),
    }


def _get_sketcher_next_reset():
    # Direct port of ajax_resetstatus.jsp's own Calendar arithmetic:
    # starting from the coming midnight, step backward by
    # SKETCHER_RESET_FREQ_HOURS repeatedly, keeping each candidate as the
    # answer, until stepping back further would land at or before now -
    # i.e. the smallest of those hour-boundaries that's still in the
    # future. Only meaningful once something actually consumes
    # SKETCHER_RESET_KEY_PATH on a matching schedule (see this module's
    # own top comment) - until then this is a correctly-computed
    # countdown to a reset that won't actually happen.
    freq_hours = settings.SKETCHER_RESET_FREQ_HOURS
    if not freq_hours or freq_hours <= 0:
        return None
    now = timezone.now()
    midnight_tonight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    candidate = midnight_tonight
    next_reset = candidate
    while candidate > now:
        next_reset = candidate
        candidate -= timedelta(hours=freq_hours)
    return next_reset


class SketcherAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Gates every Sketcher admin view behind is_sketcher_mod - set directly
    via the Django admin, not through any in-app nomination/voting flow
    (unlike the pre-2017 sketcheradmins/sketcheradminvotes tables this
    replaces). raise_exception so a logged-in user who simply isn't an
    admin gets a plain 403, rather than UserPassesTestMixin's default of
    bouncing them to the login page they're already past.
    """
    raise_exception = True

    def test_func(self):
        return self.request.user.is_sketcher_mod


class SketcherAdminView(SketcherAdminRequiredMixin, TemplateView):
    """
    The admin page itself - computes every section's data directly for
    the initial render (same as the old admin.jsp's own <jsp:include>s),
    with the sibling AJAX views below re-serving the same partials for
    each section's independent polling refresh.
    """
    template_name = 'sketcher/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sketcher_users'] = _read_sketcher_user_names()
        context['sketcher_log_lines'] = _tail_sketcher_log()
        context.update(_sketcher_reset_status_context())
        context['sketcher_banned'] = Ban.objects.select_related('user', 'banned_by').order_by('user__username')
        context['sketcher_admins'] = get_user_model().objects.filter(is_sketcher_mod=True).order_by('username')
        return context


class SketcherAdminUsersView(SketcherAdminRequiredMixin, TemplateView):
    template_name = 'sketcher/admin/users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sketcher_users'] = _read_sketcher_user_names()
        return context


class SketcherAdminKickView(SketcherAdminRequiredMixin, View):
    def post(self, request):
        username = request.POST.get('username', '').strip()
        if not username:
            return HttpResponse('')
        # sketcher-server's talk.txt protocol splits the line on
        # whitespace and requires exactly two tokens ("kick" + the name),
        # matching it against a connected user's name field exactly
        # (ServerContext.java) - a name containing a space (e.g. a site
        # username like "Brian Tiemann", which sketcher-web already uses
        # as the nickname) produces three-plus tokens and silently fails
        # to match anyone. Pre-existing protocol limitation, not
        # introduced here - flagged rather than worked around, since
        # fixing it means changing the Java server's own parsing.
        _write_sketcher_talk_line('kick {0}'.format(username))
        return HttpResponse('Kicking {0}...'.format(username))


class SketcherAdminBroadcastView(SketcherAdminRequiredMixin, View):
    def post(self, request):
        text = request.POST.get('text', '').strip()
        if not text:
            return HttpResponse('')
        # Any talk.txt line that isn't exactly "quad" or "kick <user>"
        # (and doesn't start with "/") gets broadcast verbatim to every
        # connected client as a chat message (ServerContext.java) - same
        # mechanism the old JSP's "echo" function used, attributed the
        # same way ("ADMIN (name): text").
        _write_sketcher_talk_line('ADMIN ({0}): {1}'.format(request.user.username, text))
        return HttpResponse('')


class SketcherAdminLogView(SketcherAdminRequiredMixin, TemplateView):
    template_name = 'sketcher/admin/log.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sketcher_log_lines'] = _tail_sketcher_log()
        return context


class SketcherAdminResetStatusView(SketcherAdminRequiredMixin, TemplateView):
    template_name = 'sketcher/admin/reset_status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_sketcher_reset_status_context())
        return context


class SketcherAdminToggleResetView(SketcherAdminRequiredMixin, View):
    """
    Writes/deletes SKETCHER_RESET_KEY_PATH - the exact mechanism the old
    JSP admin used (Sketcher/resetkey/resetkey), just with nothing reading
    it yet. See this module's own top comment.
    """
    def post(self, request):
        if not settings.SKETCHER_RESET_KEY_PATH:
            return HttpResponse('', status=200)
        action = request.POST.get('action')
        if action == 'cancel':
            try:
                with open(settings.SKETCHER_RESET_KEY_PATH, 'w') as f:
                    f.write(request.user.username)
            except OSError as e:
                # Unlike talk.txt/user.txt (which always exist and only
                # ever get rewritten in place), this file may not exist
                # yet - *creating* it needs write permission on its
                # containing directory, not just the file itself. If
                # that's missing, surface it clearly here rather than let
                # it become another silent, undiagnosable no-op like the
                # talk.txt bug this module's own top comment describes.
                logger.warning('Could not write %s: %s', settings.SKETCHER_RESET_KEY_PATH, e)
                return HttpResponse('Could not cancel the reset - check permissions on the sketcher-server directory.', status=500)
            # See _make_group_writable's own comment - same reasoning
            # applies here, pre-emptively, for whatever eventually
            # consumes this file on a matching cron schedule.
            _make_group_writable(settings.SKETCHER_RESET_KEY_PATH)
        elif action == 'uncancel':
            try:
                os.remove(settings.SKETCHER_RESET_KEY_PATH)
            except FileNotFoundError:
                pass
            except OSError as e:
                # Deleting is also a directory-write operation, same as
                # creating above - same reasoning, same failure mode.
                logger.warning('Could not remove %s: %s', settings.SKETCHER_RESET_KEY_PATH, e)
                return HttpResponse('Could not uncancel the reset - check permissions on the sketcher-server directory.', status=500)
        return HttpResponse('')


class SketcherAdminBannedView(SketcherAdminRequiredMixin, TemplateView):
    template_name = 'sketcher/admin/banned.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sketcher_banned'] = Ban.objects.select_related('user', 'banned_by').order_by('user__username')
        return context


class SketcherAdminBanView(SketcherAdminRequiredMixin, View):
    def post(self, request):
        username = request.POST.get('username', '').strip()
        reason = request.POST.get('reason', '').strip()
        User = get_user_model()
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse('No such user: {0}'.format(username), status=404)
        ban, created = Ban.objects.get_or_create(
            user=target,
            defaults={'banned_by': request.user, 'ban_reason': reason},
        )
        if not created:
            return HttpResponse('{0} is already banned.'.format(target.username))
        return HttpResponse('Banned {0}.'.format(target.username))


class SketcherAdminUnbanView(SketcherAdminRequiredMixin, View):
    def post(self, request):
        ban_id = request.POST.get('ban_id')
        # Unlike the old JSP (which only let the artist who placed a ban
        # lift it themselves - sketcherbannedby == artist.artistid), any
        # admin can lift any ban here. That old restriction reads like an
        # accident of the era rather than a deliberate policy - nothing
        # else about this page assumes admins operate in isolation from
        # each other (the "E-mail all" admin list exists precisely so
        # they can coordinate).
        Ban.objects.filter(id=ban_id).delete()
        return HttpResponse('')


class SketcherAdminAdminsView(SketcherAdminRequiredMixin, TemplateView):
    template_name = 'sketcher/admin/admins.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sketcher_admins'] = get_user_model().objects.filter(is_sketcher_mod=True).order_by('username')
        return context
