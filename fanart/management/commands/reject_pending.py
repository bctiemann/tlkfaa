from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import fnmatch
import unicodedata, re

import logging
logger = logging.getLogger(__name__)

from fanart import models, tasks


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--pending_id',
                    dest='pending_id',
                    default=None)
        parser.add_argument('--reason',
                    dest='reason',
                    default='reupload')

    def handle(self, *args, **options):

        pending_id = options.get('pending_id')
        reason = options.get('reason')

        pending = models.Pending.objects.get(pk=pending_id)

        send_email = False
        if reason == 'copied':
            subject = 'Fan Art Submission (unable to accept)'
            text_template = 'email/approval/rejected_copied.txt'
            html_template = 'email/approval/rejected_copied.html'
            send_email = True
        if reason == 'off-topic':
            subject = 'Fan Art Submission (unable to accept)'
            text_template = 'email/approval/rejected_offtopic.txt'
            html_template = 'email/approval/rejected_offtopic.html'
            send_email = True
        if reason == 'inappropriate':
            subject = 'Fan Art Submission (unable to accept)'
            text_template = 'email/approval/rejected_inappropriate.txt'
            html_template = 'email/approval/rejected_inappropriate.html'
            send_email = True
        if reason == 'reupload':
            subject = u'Fan Art Submission (please re-upload {0})'.format(pending.filename)
            text_template = 'email/approval/rejected_reupload.txt'
            html_template = 'email/approval/rejected_reupload.html'
            send_email = True

        print subject

        if send_email:
            attachments = []
            with open(pending.picture.path) as file:
                image_data = file.read()
            attachments.append({'filename': pending.picture.name, 'content': image_data, 'mimetype': pending.mime_type})

            email_context = {'pending': pending}
            tasks.send_email.delay(
                recipients = [pending.artist.email],
                subject = subject,
                context = email_context,
                text_template = text_template,
                html_template = html_template,
                bcc = [settings.DEBUG_EMAIL],
                attachments = attachments,
            )

        pending.delete()

