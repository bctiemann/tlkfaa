from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import fnmatch
import unicodedata, re

import logging
logger = logging.getLogger(__name__)

from fanart import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        requiring_approval = [p.id for p in models.Pending.objects.requiring_approval()]
        for pending in models.Pending.objects.all():
            print pending.id
            if pending.id in requiring_approval:
                print '{0} requires approval'.format(pending.id)
                continue

            filename = '{0}.{1}'.format(pending.next_unique_basename, pending.extension)
            for existing_file in os.listdir(pending.artist.absolute_dir_name):
                if fnmatch.fnmatch(existing_file, '{0}.*'.format(pending.next_unique_basename)):
                    logger.error('File {0} exists, matching {1}! Skipping.'.format(existing_file, filename))
                    continue

            # if replacement, update picture record
            # else, insert picture
            defaults = {
                'artist': pending.artist,
                'filename': pending.filename,
                'title': pending.title,
                'mime_type': pending.mime_type,
                'width': pending.width,
                'height': pending.height,
                'file_size': pending.file_size,
                'date_approved': timezone.now(),
                'hash': pending.hash,
                'folder': pending.folder,
                'keywords': pending.keywords,
                'work_in_progress': pending.work_in_progress,
                'allow_comments': pending.work_in_progress,
                'is_scanned': pending.is_scanned,
                'approved_by': pending.approved_by,
            }
            if pending.replaces_picture:
                picture = pending.replaces_picture
                for key, value in defaults.iteritems():
                    setattr(picture, key, value)
                if pending.reset_upload_date:
                    picture.date_uploaded = pending.date_uploaded
                picture.date_updated = timezone.now()
                picture.save()
            else:
                defaults['date_uploaded'] = pending.date_uploaded
                picture = models.Picture.objects.create(**defaults)

            # Clear then insert picturecharacters
            # Clear then populate keywords into tags
            # If not replacement, populate unviewedpictures
            # Update artist.last_upload
            # artist.refresh_num_pictures()
            # artist.refresh_picture_ranks()
            # Move files into place
            # Send email notification
