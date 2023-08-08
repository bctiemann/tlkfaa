import os
import importlib
from zipfile import ZipFile
from pwd import getpwnam
from PIL import Image
from uuid import uuid4

from django.conf import settings
from django.core import mail
from django.template import Context
from django.template.loader import get_template
from django.apps import apps

from celery import shared_task
from celery.utils.log import get_task_logger

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

    context['admin_email'] = settings.ADMIN_EMAIL
    context['admin_name'] = settings.ADMIN_NAME

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
        logger.info('Sending email "{0}" to {1}...'.format(subject, recipient))

    connection.close()


@shared_task
def send_templated_email(
        recipients,
        context,
        from_email=settings.SITE_EMAIL,
        subject=None,
        text_template=None,
        html_template=None,
        attachments=None,
        cc=None,
        bcc=None,
):
    if settings.DEBUG:
        recipients = [settings.DEBUG_EMAIL]

    context['admin_email'] = settings.ADMIN_EMAIL
    context['admin_name'] = settings.ADMIN_NAME

    plaintext_template = get_template(text_template)
    html_template = get_template(html_template)
    bcc = bcc or []
    if settings.BCC_EMAIL:
        bcc.append(settings.BCC_EMAIL)
    connection = mail.get_connection()
    connection.open()
    for recipient in recipients:
        text_content = plaintext_template.render(context)
        html_content = html_template.render(context)
        msg = mail.EmailMultiAlternatives(subject, text_content, from_email, [recipient], cc=cc, bcc=bcc)
        msg.attach_alternative(html_content, "text/html")
        if attachments:
            for attachment in attachments:
                msg.attach(**attachment)

        msg.send()
        logger.info(f'Sent email "{subject}" to {recipient}')

    connection.close()

    return 'done'


# Canned email tasks

@shared_task
def send_comment_email(user_id, picture_id, comment_id):
    User = apps.get_model('fanart', 'User')
    Picture = apps.get_model('fanart', 'Picture')
    ThreadedComment = apps.get_model('fanart', 'ThreadedComment')

    user = User.objects.get(pk=user_id)
    picture = Picture.objects.get(pk=picture_id)
    comment = ThreadedComment.objects.get(pk=comment_id)

    email_context = {
        'user': user,
        'picture': picture,
        'comment': comment,
        'base_url': settings.SERVER_BASE_URL,
    }
    send_email(
        recipients=[picture.artist.email],
        subject='TLKFAA: New Comment Posted',
        context=email_context,
        text_template='email/comment_posted.txt',
        html_template='email/comment_posted.html',
        bcc=[settings.DEBUG_EMAIL]
    )


@shared_task
def send_shout_email(user_id, artist_id, shout_id):
    User = apps.get_model('fanart', 'User')
    Shout = apps.get_model('fanart', 'Shout')

    user = User.objects.get(pk=user_id)
    artist = User.objects.get(pk=artist_id)
    shout = Shout.objects.get(pk=shout_id)

    email_context = {'user': user, 'artist': artist, 'shout': shout}
    send_email(
        recipients=[artist.email],
        subject='TLKFAA: New Roar Posted',
        context=email_context,
        text_template='email/shout_posted.txt',
        html_template='email/shout_posted.html',
        bcc=[settings.DEBUG_EMAIL]
    )


@shared_task
def send_spam_flag_email(spam_flag_id):
    SpamFlag = apps.get_model('fanart', 'SpamFlag')

    spam_flag = SpamFlag.objects.get(pk=spam_flag_id)

    email_context = {
        'comment': spam_flag.comment or spam_flag.shout,
    }
    send_email(
        recipients=[settings.ADMIN_EMAIL],
        subject='TLKFAA: Comment flagged as spam',
        context=email_context,
        text_template='email/spam_flagged.txt',
        html_template='email/spam_flagged.html',
    )


@shared_task
def send_pending_moderation_email(pending_id, subject, text_template, html_template, attachments=None):
    Pending = apps.get_model('fanart', 'Pending')

    pending = Pending.objects.get(pk=pending_id)

    email_context = {'pending': pending}
    send_email(
        recipients=[pending.artist.email],
        subject=subject,
        context=email_context,
        text_template=text_template,
        html_template=html_template,
        bcc=[settings.DEBUG_EMAIL],
        attachments=attachments,
    )


@shared_task
def send_pending_published_email(pending_id, picture_id):
    Pending = apps.get_model('fanart', 'Pending')
    Picture = apps.get_model('fanart', 'Picture')

    pending = Pending.objects.get(pk=pending_id)
    picture = Picture.objects.get(pk=picture_id)

    subject = 'Fan-Art Picture Accepted'
    text_template = 'email/approval/approved.txt'
    html_template = 'email/approval/approved.html'

    email_context = {
        'pending': pending,
        'picture': picture,
        'base_url': settings.SERVER_BASE_URL,
    }
    send_email(
        recipients=[pending.artist.email],
        subject=subject,
        context=email_context,
        text_template=text_template,
        html_template=html_template,
        bcc=[settings.DEBUG_EMAIL]
    )


@shared_task
def send_bulletin_posted_email(bulletin_id):
    Bulletin = apps.get_model('fanart', 'Bulletin')

    bulletin = Bulletin.objects.get(pk=bulletin_id)

    email_context = {'user': bulletin.user, 'bulletin': bulletin}
    send_email(
        recipients=[settings.ADMIN_EMAIL],
        subject='TLKFAA: New Bulletin Posted',
        context=email_context,
        text_template='email/bulletin_posted.txt',
        html_template='email/bulletin_posted.html',
    )


@shared_task
def send_bulletin_reply_email(comment_id):
    ThreadedComment = apps.get_model('fanart', 'ThreadedComment')

    comment = ThreadedComment.objects.get(pk=comment_id)

    email_context = {
        'user': comment.user,
        'bulletin': comment.bulletin,
        'comment': comment.comment,
        'base_url': settings.SERVER_BASE_URL,
    }
    send_email(
        recipients=[comment.bulletin.user.email],
        subject='TLKFAA: New Bulletin Reply Posted',
        context=email_context,
        text_template='email/bulletin_comment_posted.txt',
        html_template='email/bulletin_comment_posted.html',
        # bcc=[settings.DEBUG_EMAIL]
    )


@shared_task
def send_art_trade_response_email(gift_picture_id, is_declined=False):
    GiftPicture = apps.get_model('fanart', 'GiftPicture')

    gift_picture = GiftPicture.objects.get(pk=gift_picture_id)

    email_context = {'user': gift_picture.recipient, 'giftpicture': gift_picture, 'base_url': settings.SERVER_BASE_URL}
    if is_declined:
        subject = 'TLKFAA: Art Trade/Request Rejected by {0}'.format(gift_picture.recipient.username)
        text_template = 'email/gift_rejected.txt'
        html_template = 'email/gift_rejected.html'
    else:
        subject = 'TLKFAA: Art Trade/Request Accepted by {0}'.format(gift_picture.recipient.username)
        text_template = 'email/gift_accepted.txt'
        html_template = 'email/gift_accepted.html'

    send_email(
        recipients=[gift_picture.sender.email],
        subject=subject,
        context=email_context,
        text_template=text_template,
        html_template=html_template,
        bcc=[settings.DEBUG_EMAIL]
    )


@shared_task
def send_pm_email(pm_id):
    PrivateMessage = apps.get_model('fanart', 'PrivateMessage')

    pm = PrivateMessage.objects.get(pk=pm_id)

    email_context = {'pm': pm, 'sender': pm.sender, 'base_url': settings.SERVER_BASE_URL}
    subject = 'TLKFAA Private Message from {0}'.format(pm.sender.username)
    send_email(
        recipients=[pm.recipient.email],
        subject=subject,
        context=email_context,
        text_template='email/pm_sent.txt',
        html_template='email/pm_sent.html',
        bcc=[settings.DEBUG_EMAIL]
    )


# Image processing

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
        if not picture_object.picture.name:
            image_error = 'Pending {0} has no name; exiting'.format(picture_object)
            logger.error(image_error)
            mail.mail_admins('Image processing error', image_error)
            return None, None
        image_path = '{0}/{1}'.format(settings.MEDIA_ROOT, picture_object.picture.name)
        if thumb_size == 'small':
            new_image_path = picture_object.thumbnail_path
        elif thumb_size == 'large':
            new_image_path = picture_object.preview_path
        orig_height = picture_object.height
        orig_width = picture_object.width
    elif model == 'User':
        if not picture_object.profile_picture.name:
            image_error = 'Profile picture {0} has no name; exiting'.format(picture_object)
            logger.error(image_error)
            mail.mail_admins('Image processing error', image_error)
            return None, None
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
        if not picture_object.showcase_picture.name:
            image_error = 'Featured artist picture {0} has no name; exiting'.format(picture_object)
            logger.error(image_error)
            mail.mail_admins('Image processing error', image_error)
            return None, None
        image_path = '{0}/{1}'.format(settings.MEDIA_ROOT, picture_object.showcase_picture.name)
        new_image_path = picture_object.thumbnail_path
        orig_height = picture_object.height
        orig_width = picture_object.width

    if not os.path.exists(image_path):
        logger.error('{0} not found. Possibly already deleted.'.format(image_path))
        return None, None

    try:
        im = Image.open(image_path)
        im.thumbnail((max_pixels, max_pixels * orig_height / orig_width))
    except IOError as e:
        image_error = '{0} - {1} - {2}'.format(picture_object, e, image_path)
        logger.error(image_error)
        mail.mail_admins('Image processing error', image_error)

        if model == 'Pending' and not picture_object.failed_processing:
            email_context = {
                'user': picture_object.artist,
                'pending': picture_object,
            }
            send_email(
                recipients=[picture_object.artist.email],
                subject='TLKFAA: Image processing error',
                context=email_context,
                text_template='email/approval/rejected_reupload.txt',
                html_template='email/approval/rejected_reupload.html',
            )
            picture_object.failed_processing = True
            picture_object.save()

        return None, None

    if getattr(picture_object, 'THUMBNAILS_JPEG', True) == True:
        format = 'JPEG'
        mode = 'RGB'
    else:
        format = im.format
        mode = im.mode

    logger.info('{0} {1}'.format(mode, format))
    im_new = Image.new(mode, im.size)
    im_new.paste(im)
    im_new.save(new_image_path, format)

    www_uid = getpwnam(settings.WWW_USER).pw_uid
    try:
        os.chown(new_image_path, www_uid, -1)
    except OSError:
        pass

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
#     print(models)
#     print(model)
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


@shared_task
def zip_pictures(artist_id):
    from fanart.models import User
    artist = User.objects.get(pk=artist_id)

    hash = uuid4()
    zip_dir = f'{settings.MEDIA_ROOT}/zips/{hash}'
    try:
        os.makedirs(zip_dir)
    except OSError:
        pass

    os.chdir(artist.absolute_dir_name)

    zip_file = f'{zip_dir}/{artist.dir_name}.zip'
    with ZipFile(zip_file, 'w') as artist_zip:
        for picture in artist.picture_set.all():
            artist_zip.write(picture.filename)

    zip_url = f'{settings.SERVER_BASE_URL}{settings.MEDIA_URL}zips/{hash}/{artist.dir_name}.zip'

    email_context = {
        'user': artist,
        'zip_url': zip_url,
    }
    send_email(
        recipients=[artist.email],
        subject='TLKFAA: Gallery Archive Completed',
        context=email_context,
        text_template='email/zipfile_created.txt',
        html_template='email/zipfile_created.html',
        bcc=[settings.DEBUG_EMAIL],
    )
