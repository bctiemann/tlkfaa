from django.conf import settings
from django.core import mail
from django.template import Context
from django.template.loader import get_template

from celery import shared_task
from celery.utils.log import get_task_logger

from PIL import Image
import os


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

def create_thumbnail(model, picture_object, thumb_size):
    max_pixels = settings.THUMB_SIZE[thumb_size]
    logger.info('Creating {0} px thumb for {1} {2}'.format(max_pixels, model, picture_object.id))

    if model == 'TradingClaim':
        image_path = '{0}/Artwork/claims/{1}.{2}'.format(settings.MEDIA_ROOT, picture_object.id, picture_object.extension)
        new_image_path = '{0}/Artwork/claims/{1}.s.jpg'.format(settings.MEDIA_ROOT, picture_object.id)
    elif model == 'ColoringPicture':
        image_path = '{0}/Artwork/coloring/{1}.{2}'.format(settings.MEDIA_ROOT, picture_object.id, picture_object.extension)
        new_image_path = '{0}/Artwork/coloring/{1}.s.jpg'.format(settings.MEDIA_ROOT, picture_object.id)

    im = Image.open(image_path)
    im.thumbnail((max_pixels, max_pixels * picture_object.height / picture_object.width))
    im.save(new_image_path, im.format)

    return im.size

@shared_task
def create_thumbnails(model, object_id):
    from fanart import models
    model_class = getattr(models, model)
    picture_object = model_class.objects.get(pk=object_id)
    width, height = create_thumbnail(model, picture_object, 'small')
#    picture_object.width_thumb_small, picture_object.height_thumb_small = create_thumbnail(picture_object, 'small')
#    picture_object.width_thumb_large, picture_object.height_thumb_large = create_thumbnail(picture_object, 'large')
#    picture_object.thumb_small = '{0}/{1}'.format(settings.THUMB_SIZE['small'], picture_object.file.name)
#    picture_object.thumb_large = '{0}/{1}'.format(settings.THUMB_SIZE['large'], picture_object.file.name)
    picture_object.generated_thumbs = True
    picture_object.save(update_thumbs=False)

