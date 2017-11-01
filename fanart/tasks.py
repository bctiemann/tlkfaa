from django.conf import settings
from django.core import mail
from django.template import Context
from django.template.loader import get_template

from celery import shared_task

import logging
logger = logging.getLogger(__name__)


TEXT_TEMPLATE = 'email/notification.txt'
HTML_TEMPLATE = 'email/notification.html'
FROM_ADDRESS = settings.SITE_EMAIL


@shared_task
def send_email(recipients,
    subject,
    context,
    text_template=TEXT_TEMPLATE,
    html_template=HTML_TEMPLATE,
    attachments=None,
    bcc=[],
):
    if settings.DEBUG:
        recipients = [settings.DEBUG_EMAIL]

    plaintext = get_template(text_template)
    htmly = get_template(html_template)
    connection = mail.get_connection()
    connection.open()
    for recipient in recipients:
        text_content = plaintext.render(context)
        html_content = htmly.render(context)
        msg = mail.EmailMultiAlternatives(subject, text_content, FROM_ADDRESS, [recipient], bcc=bcc)
        msg.attach_alternative(html_content, "text/html")
        if attachments:
            for attachment in attachments:
                msg.attach(**attachment)

        msg.send()

    connection.close()

