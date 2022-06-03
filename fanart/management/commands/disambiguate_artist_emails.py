import MySQLdb
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from fanart import models as fanart_models

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key',)

    def handle(self, *args, **options):
        db = MySQLdb.connect(
            passwd=settings.DATABASES['legacy']['PASSWORD'],
            db=settings.DATABASES['legacy']['NAME'],
            host=settings.DATABASES['legacy']['HOST'],
            user=settings.DATABASES['legacy']['USER'],
            charset=settings.DATABASES['legacy']['OPTIONS']['charset'],
        )
        c = db.cursor(MySQLdb.cursors.DictCursor)

        count = 0
        for user in fanart_models.User.objects.filter(artist_id_orig__isnull=False):
            c.execute("""SELECT * FROM artists WHERE artistid=%s""", (user.artist_id_orig,))
            for old_artist in c.fetchall():
                if old_artist['email'] and user.email != old_artist['email']:
                    print(user)
                    print(old_artist['email'].encode('utf8'))
                    count += 1

#                    replace_input = raw_input('\nUpdate email to {0} ? '.format(old_artist['email'].encode('utf8')))
#                    if replace_input.lower() == 'y':
                    if True:
                        print('Replacing')
                        user.email = old_artist['email']
                        user.save()
                    else:
                        print('Skipping')
                    print('')
        print(count)
