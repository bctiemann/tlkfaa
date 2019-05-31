from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import six, timezone

import os
import unicodedata, re
import MySQLdb

import logging
logger = logging.getLogger(__name__)

from fanart import models as fanart_models
from trading_tree.models import Offer, Claim
from coloring_cave.models import Base, ColoringPicture
from pms.models import PrivateMessage


class Command(BaseCommand):

    def handle(self, *args, **options):

        for pm in PrivateMessage.objects.all():
            root_pm = pm
            while root_pm.reply_to:
                root_pm = root_pm.reply_to
            print(pm.id, root_pm.id)
            pm.root_pm = root_pm
            pm.save()
