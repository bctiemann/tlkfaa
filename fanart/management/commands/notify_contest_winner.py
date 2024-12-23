import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.urls import reverse

from fanart import models, tasks

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        latest_contest = models.Contest.objects.filter(type='global').order_by('-date_created').first()
        if latest_contest.is_ended:
            entry_notified = False
            for entry in latest_contest.winning_entries:
                print(entry.votes, latest_contest.total_votes)
                if entry_notified:
                    continue
                if entry.date_notified is None or (timezone.now() - entry.date_notified).days < 3:
                    entry_notified = True
                    if entry.date_notified is None:
                        entry.date_notified = timezone.now()
                        entry.save()

                    vote_percent = int(float(entry.votes) / float(latest_contest.total_votes) * 100) if latest_contest.total_votes else 100

                    email_context = {
                        'entry': entry,
                        'contest': latest_contest,
                        'vote_percent': vote_percent,
                        'base_url': settings.SERVER_BASE_URL,
                        'url': reverse('contest-setup'),
                        'admin_email': settings.ADMIN_EMAIL,
                    }
                    text_template = 'email/contest_winner.txt'
                    html_template = 'email/contest_winner.html'
                    subject = 'Archive-Wide Art Contest Winner!'
                    tasks.send_email(
                        recipients=[entry.picture.artist.email],
                        subject=subject,
                        context=email_context,
                        text_template=text_template,
                        html_template=html_template,
                        bcc=[settings.DEBUG_EMAIL]
                    )
