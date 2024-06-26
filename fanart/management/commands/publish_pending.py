import os
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)

from fanart import models, tasks


class Command(BaseCommand):

    def handle(self, *args, **options):
        for pending in models.Pending.objects.all():
            print(pending.id)

            try:
                pending.picture.file
            except (FileNotFoundError, ValueError):
                pending.picture = None
                pending.failed_processing = True
                pending.save()
                print('{0} file is missing; setting to failed processing'.format(pending.id))
                continue

            if pending in models.Pending.objects.requiring_approval():
                print('{0} requires approval'.format(pending.id))
                continue

            if not pending.thumbnail_created or not pending.preview_created:
                print('{0} thumbnails still processing'.format(pending.id))
                continue

            if pending.locked_for_publish:
                print('{0} locked for publish'.format(pending.id))
                continue

            filename = '{0}.{1}'.format(pending.next_unique_basename, pending.extension)
            if os.path.isfile('{0}/{1}.s.jpg'.format(pending.artist.absolute_dir_name, pending.next_unique_basename)):
                logger.error('File {0} exists; skipping.'.format(pending.next_unique_basename))
                continue

            pending.locked_for_publish = True
            pending.filename = filename
            pending.save()

            # if replacement, update picture record
            # else, insert picture
            defaults = {
                'artist': pending.artist,
                'filename': pending.filename,
                'original_filename': pending.original_filename,
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
                'allow_comments': pending.allow_comments,
                'is_scanned': pending.is_scanned,
                'approved_by': pending.approved_by,
            }
            if pending.replaces_picture:
                original_path = pending.replaces_picture.path
                original_thumbnail_path = pending.replaces_picture.thumbnail_path
                original_preview_path = pending.replaces_picture.preview_path

                picture = pending.replaces_picture
                for key, value in defaults.items():
                    setattr(picture, key, value)
                if pending.reset_upload_date:
                    picture.date_uploaded = pending.date_uploaded
                picture.date_updated = timezone.now()
                picture.save()
            else:
                defaults['date_uploaded'] = pending.date_uploaded
                picture = models.Picture.objects.create(**defaults)

            # Clear then insert picturecharacters
            picture.picturecharacter_set.all().delete()
            for pc in pending.picturecharacter_set.all():
                pc.pending = None
                pc.picture = picture
                pc.save()
                pc.character.refresh_num_pictures()

            # Clear then populate keywords into tags
            picture.tags.clear()
            for keyword in pending.keywords.split(','):
                if keyword:
                    tag, is_created = models.Tag.objects.get_or_create(tag=keyword)
                    picture.tags.add(tag)

            # If not a replacement or notify_fans_of_replacement is on, populate unviewedpictures
            if not pending.replaces_picture or pending.notify_fans_of_replacement:
                for watcher in pending.artist.fans.all():
                    uvp = models.UnviewedPicture.objects.create(
                        picture = picture,
                        artist = picture.artist,
                        user = watcher.user,
                    )

            # Update artist.last_upload
            pending.artist.last_upload = timezone.now()

            # Refresh num_pictures and picture ranks in artist and folder
            pending.artist.refresh_num_pictures()
            pending.artist.refresh_picture_ranks()
            if pending.folder:
                pending.folder.refresh_num_pictures()
                pending.folder.refresh_picture_ranks()
            else:
                pending.artist.refresh_main_folder_picture_ranks()

            # Move files into place
            if pending.replaces_picture:
                try:
                    os.remove(original_path)
                    os.remove(original_thumbnail_path)
                    os.remove(original_preview_path)
                except OSError:
                    pass

            os.rename(pending.picture.path, picture.path)
            os.rename(pending.thumbnail_path, picture.thumbnail_path)
            os.rename(pending.preview_path, picture.preview_path)
            os.rmdir(os.path.dirname(pending.picture.path))

            # Detect and save image type
            picture.update_type()

            # Send email notification
            if pending.notify_on_approval:
                tasks.send_pending_published_email(pending.id, picture.id)

            # delete pending
            pending.delete()
