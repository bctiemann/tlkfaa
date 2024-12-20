from datetime import timedelta
import logging

from django.http import Http404
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.utils import timezone
from django.shortcuts import reverse, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from fanart.views import UserPaneMixin
from fanart import forms
from fanart.models import Contest, ContestEntry, ContestVote, Picture
from fanart.utils import PagesLink

logger = logging.getLogger(__name__)


# Contests

class ContestsView(UserPaneMixin, ListView):
    template_name = 'fanart/chamber_of_stars/contests.html'
    model = Contest
    current_contest = None
    sort_by = None
    paginate_by = 20

    def get_queryset(self):
        self.current_contest = Contest.objects.filter(
            type='global', date_start__lt=timezone.now(), is_active=True
        ).order_by('-date_created').first()

        queryset = Contest.objects.filter(is_active=True).exclude(pk=self.current_contest.pk)

        self.sort_by = self.request.GET.get('sort_by', None)
        if self.sort_by not in ['artist', 'startdate', 'deadline']:
            self.sort_by = 'startdate'

        order_by_map = {
            'artist': 'creator__username',
            'startdate': '-date_start',
            'deadline': '-date_end',
        }
        queryset = queryset.order_by(order_by_map[self.sort_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_contest'] = self.current_contest
        context['sort_by'] = self.sort_by

        page_obj = context['page_obj']
        context['pages_link'] = PagesLink(
            len(self.object_list),
            self.paginate_by,
            page_obj.number,
            is_descending=True,
            base_url=self.request.path,
            query_dict=self.request.GET,
        )

        return context


class ContestsGlobalView(ContestsView):

    def get_queryset(self):
        contests = super().get_queryset()
        return contests.filter(type='global')


class ContestsPersonalView(ContestsView):

    def get_queryset(self):
        contests = super().get_queryset()
        contests = contests.filter(type='personal')
        personal_account_deadline_cutoff_date = timezone.now() - timedelta(days=2)
        return contests.filter(date_end__gte=personal_account_deadline_cutoff_date)


class ContestView(UserPaneMixin, DetailView):
    template_name = 'fanart/chamber_of_stars/contest.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Contest, pk=self.kwargs['contest_id'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super(ContestView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['my_entries'] = self.object.contestentry_set.filter(picture__artist=self.request.user).all()
            context['my_vote'] = ContestVote.objects.filter(
                user=self.request.user, entry__contest=self.object
            ).first()

        return context


class ContestEntryCreateView(LoginRequiredMixin, CreateView):
    model = ContestEntry
    form_class = forms.ContestEntryForm
    template_name = 'fanart/chamber_of_stars/contest.html'

    def form_valid(self, form):
        contest = get_object_or_404(Contest, pk=self.kwargs.get('contest_id', None))
        picture = get_object_or_404(Picture, pk=self.request.POST.get('picture', None), artist=self.request.user)

        already_entered = contest.contestentry_set.filter(picture__artist=self.request.user).exists()
        if not contest.allow_multiple_entries and already_entered:
            logger.info(f'{self.request.user} already has an entry in {contest}')
            return redirect(reverse('contest', kwargs={'contest_id': contest.id}))

        contest_entry = form.save(commit=False)
        contest_entry.user = self.request.user
        contest_entry.contest = contest
        contest_entry.picture = picture
        contest_entry.save()
        logger.info(f'{self.request.user} entered {picture} in {contest}')
        response = super(ContestEntryCreateView, self).form_valid(form)
        return response


class ContestEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = ContestEntry

    def get_object(self, queryset=None):
        return get_object_or_404(
            ContestEntry,
            (Q(picture__artist=self.request.user) | Q(contest__creator=self.request.user)),
            pk=self.kwargs['entry_id'],
        )

    def get_success_url(self):
        return reverse('contest', kwargs={'contest_id': self.object.contest.id})


class ContestVoteView(LoginRequiredMixin, CreateView):
    model = ContestVote
    form_class = forms.ContestVoteForm
    template_name = 'fanart/chamber_of_stars/contest.html'

    def form_valid(self, form):
        ContestVote.objects.filter(
            entry__contest=form.cleaned_data['entry'].contest, user=self.request.user
        ).delete()

        contest_vote = form.save(commit=False)
        contest_vote.user = self.request.user
        contest_vote.save()

        response = super(ContestVoteView, self).form_valid(form)
        return response


class ContestSetupView(LoginRequiredMixin, UserPaneMixin, CreateView):
    model = Contest
    template_name = 'fanart/chamber_of_stars/contest_setup.html'
    form_class = forms.GlobalContestForm

    def get_context_data(self, **kwargs):
        context = super(ContestSetupView, self).get_context_data(**kwargs)

        latest_contest = Contest.objects.filter(type='global').order_by('-date_created').first()
        if not latest_contest.is_ended:
            raise Http404

        winning_entry = None
        for entry in latest_contest.winning_entries:
            if entry.date_notified:
                winning_entry = entry

        if not winning_entry or winning_entry.picture.artist != self.request.user:
            raise Http404

        context['latest_contest'] = latest_contest

        return context

    def form_valid(self, form):
        logger.info(self.request.POST)
        logger.info(form.cleaned_data)

        contest = form.save(commit=False)
        contest.creator = self.request.user
        contest.type = 'global'
        contest.allow_voting = True

#        length_days = int(self.request.POST.get('length_days', 7))
        length_days = int(form.cleaned_data['length_days'])
        tonight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        contest.date_start = tonight
        date_end = tonight + timedelta(days=length_days)
        contest.date_end = date_end

        contest.save()

        response = super(ContestSetupView, self).form_valid(form)
        return response

    def get_success_url(self):
        return reverse('contest-setup-success')


class ContestSetupSuccessView(LoginRequiredMixin, TemplateView):
    model = Contest
    template_name = 'fanart/chamber_of_stars/contest_setup_success.html'

    def get_context_data(self, **kwargs):
        context = super(ContestSetupSuccessView, self).get_context_data(**kwargs)

        latest_contest = Contest.objects.filter(type='global').order_by('-date_created').first()
        if latest_contest.is_ended or latest_contest.creator != self.request.user:
            raise Http404

        context['latest_contest'] = latest_contest

        return context
