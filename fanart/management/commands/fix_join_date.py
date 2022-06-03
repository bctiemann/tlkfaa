import MySQLdb
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from fanart import models as fanart_models

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        db = MySQLdb.connect(
            passwd=settings.DATABASES['legacy']['PASSWORD'],
            db=settings.DATABASES['legacy']['NAME'],
            host=settings.DATABASES['legacy']['HOST'],
            user=settings.DATABASES['legacy']['USER'],
            charset=settings.DATABASES['legacy']['OPTIONS']['charset'],
        )
        c = db.cursor(MySQLdb.cursors.DictCursor)

        for user in fanart_models.User.objects.all():
            user_old = None
            artist_old = None
            if user.id_orig:
                c.execute("""SELECT created FROM users WHERE userid = {0}""".format(user.id_orig))
                user_old = c.fetchone()
            if user.artist_id_orig:
                c.execute("""SELECT created FROM artists WHERE artistid = {0}""".format(user.artist_id_orig))
                artist_old = c.fetchone()

#            if user_old and user_old['created'] == None and artist_old and artist_old['created'] == None:
            if artist_old and artist_old['created'] == None:
                print(user.username.encode('utf8'), user.id, user.date_joined, user_old, artist_old)
                user.date_joined = '1970-01-01'
                user.save()
