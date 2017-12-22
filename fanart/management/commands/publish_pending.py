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
            if pending.replaces_picture:
                pending.replaces_picture.filename = filename
                pending.replaces_picture.title = pending.title
                pending.replaces_picture.mime_type = pending.mime_type
                pending.replaces_picture.date_inserted = timezone.now()
                pending.replaces_picture.date_updated = timezone.now()
                if pending.reset_upload_date:
                    pending.replaces_picture.date_uploaded = pending.date_uploaded
                pending.replaces_picture.hash = pending.hash
                pending.replaces_picture.folder = pending.folder
                pending.replaces_picture.keywords = pending.keywords
                pending.replaces_picture.work_in_progress = pending.work_in_progress
                pending.replaces_picture.allow_comments = pending.allow_comments
                pending.replaces_picture.is_scanned = pending.is_scanned
                pending.replaces_picture.save()

            # else, insert picture
            # Clear then insert picturecharacters
            # Clear then populate keywords into tags
            # If not replacement, populate unviewedpictures
            # Update artist.last_upload
            # artist.refresh_num_pictures()
            # artist.refresh_picture_ranks()
            # Move files into place
            # Send email notification
