from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone
from django.urls import reverse

import logging
logger = logging.getLogger(__name__)

from fanart import models, tasks


class Command(BaseCommand):

    def handle(self, *args, **options):
        latest_contest = models.Contest.objects.filter(type='global').order_by('-date_created').first()
        if latest_contest.is_ended:
            entry_notified = False
            for entry in latest_contest.winning_entries:
                if entry_notified:
                    continue
                if entry.date_notified == None or (timezone.now() - entry.date_notified).days < 3:
                    print(entry, entry.num_votes)
                    entry_notified = True
                    if entry.date_notified == None:
                        entry.date_notified = timezone.now()
                        entry.save()

                    email_context = {
                        'entry': entry,
                        'contest': latest_contest,
                        'vote_percent': int(float(entry.votes) / float(latest_contest.total_votes) * 100),
                        'base_url': settings.SERVER_BASE_URL,
                        'url': reverse('contest-setup'),
                        'admin_email': settings.ADMIN_EMAIL,
                    }
                    text_template = 'email/contest_winner.txt'
                    html_template = 'email/contest_winner.html'
                    subject = 'Archive-Wide Art Contest Winner!'
                    tasks.send_email.delay(
                        recipients=[entry.picture.artist.email],
                        subject=subject,
                        context=email_context,
                        text_template=text_template,
                        html_template=html_template,
                        bcc=[settings.DEBUG_EMAIL]
                    )

