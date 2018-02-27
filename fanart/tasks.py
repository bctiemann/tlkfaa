from django.conf import settings
from django.core import mail
from django.template import Context
from django.template.loader import get_template

from celery import shared_task
from celery.utils.log import get_task_logger

from PIL import Image
import os
import importlib
from pwd import getpwnam

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

def create_thumbnail(model, picture_object, thumb_size, **kwargs):
    max_pixels = settings.THUMB_SIZE[thumb_size]
    logger.info('Creating {0} px thumb for {1} {2}'.format(max_pixels, model, picture_object.id))

    if model == 'Offer':
        image_path = '{0}/Artwork/offers/{1}.{2}'.format(settings.MEDIA_ROOT, picture_object.id, picture_object.extension)
        if thumb_size == 'offer':
            new_image_path = picture_object.thumbnail_path
        elif thumb_size == 'large':
            new_image_path = picture_object.preview_path
#        new_image_path = '{0}/Artwork/offers/{1}.s.jpg'.format(settings.MEDIA_ROOT, picture_object.id)
        orig_height = picture_object.height
        orig_width = picture_object.width
    if model == 'Claim':
        image_path = '{0}/Artwork/claims/{1}.{2}'.format(settings.MEDIA_ROOT, picture_object.id, picture_object.extension)
        if thumb_size == 'small':
            new_image_path = picture_object.thumbnail_path
        elif thumb_size == 'large':
            new_image_path = picture_object.preview_path
#        new_image_path = '{0}/Artwork/claims/{1}.s.jpg'.format(settings.MEDIA_ROOT, picture_object.id)
        orig_height = picture_object.height
        orig_width = picture_object.width
    elif model == 'ColoringPicture':
        image_path = '{0}/Artwork/coloring/{1}.{2}'.format(settings.MEDIA_ROOT, picture_object.id, picture_object.extension)
        if thumb_size == 'small':
            new_image_path = picture_object.thumbnail_path
        elif thumb_size == 'large':
            new_image_path = picture_object.preview_path
        orig_height = picture_object.height
        orig_width = picture_object.width
    elif model == 'Pending':
        image_path = '{0}/{1}'.format(settings.MEDIA_ROOT, picture_object.picture.name)
        if thumb_size == 'small':
            new_image_path = picture_object.thumbnail_path
        elif thumb_size == 'large':
            new_image_path = picture_object.preview_path
        orig_height = picture_object.height
        orig_width = picture_object.width
    elif model == 'User':
        image_path = '{0}/{1}'.format(settings.MEDIA_ROOT, picture_object.profile_picture.name)
        filename_parts = picture_object.profile_picture.name.split('.')
        basename = '.'.join(filename_parts[:-1])
        extension = filename_parts[-1].lower()
        if thumb_size == 'small':
            new_image_path = '{0}/{1}.s.{2}'.format(settings.MEDIA_ROOT, basename, extension)
        else:
            new_image_path = image_path
        orig_height = picture_object.profile_height
        orig_width = picture_object.profile_width
    elif model == 'FeaturedArtistPicture':
        image_path = '{0}/{1}'.format(settings.MEDIA_ROOT, picture_object.showcase_picture.name)
        new_image_path = picture_object.thumbnail_path
        orig_height = picture_object.height
        orig_width = picture_object.width

    if not os.path.exists(image_path):
        logger.error('{0} not found. Possibly already deleted.'.format(image_path))
        return None, None

    try:
        im = Image.open(image_path)
    except IOError, e:
        logger.error(e)
        return None, None

    im.thumbnail((max_pixels, max_pixels * orig_height / orig_width))

    if getattr(picture_object, 'THUMBNAILS_JPEG', True) == True:
        format = 'JPEG'
        mode = 'RGB'
    else:
        format = im.format
        mode = im.mode

    im_new = Image.new(mode, im.size, (255,255,255))
    im_new.paste(im)
    im_new.save(new_image_path, format)

    www_uid = getpwnam(settings.WWW_USER).pw_uid
    os.chown(new_image_path, www_uid, -1)

    return im.size

def resize_image(model, picture_object, thumb_size):
    logger.info('Resizing {0} {1} to {2} px'.format(model, picture_object.id, max_pixels))
    max_pixels = settings.IMAGE_SIZE[model]

    if model == 'User':
        pass

    return None, None

@shared_task
def process_images(model_class_path, model, object_id, thumb_size='small'):
    models = importlib.import_module(model_class_path)
#    model_class = getattr(importlib.import_module(model_class_path), model)
#    from model_app import models
    print models
    print model
    model_class = getattr(models, model)

    try:
        picture_object = model_class.objects.get(pk=object_id)
    except model_class.DoesNotExist:
        return None

    width, height = create_thumbnail(model, picture_object, thumb_size, kwargs=None)
#    picture_object.width_thumb_small, picture_object.height_thumb_small = create_thumbnail(picture_object, 'small')
#    picture_object.width_thumb_large, picture_object.height_thumb_large = create_thumbnail(picture_object, 'large')
#    picture_object.thumb_small = '{0}/{1}'.format(settings.THUMB_SIZE['small'], picture_object.file.name)
#    picture_object.thumb_large = '{0}/{1}'.format(settings.THUMB_SIZE['large'], picture_object.file.name)
#    picture_object.generated_thumbs = True
    return picture_object.save(update_thumbs=False)

#@shared_task
#def resize_image(model, object_id):
