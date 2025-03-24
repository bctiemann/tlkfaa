import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from fanart.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        one_week_ago = timezone.now() - timedelta(days=7)
        for artist in User.objects.filter(last_upload__gte=one_week_ago):
            most_recent_picture = artist.picture_set.order_by('-date_approved').first()
            if not most_recent_picture:
                continue
            if most_recent_picture.date_approved > artist.last_upload:
                print(f'{artist} last_upload: {artist.last_upload}, latest_picture: {most_recent_picture.date_approved}')
