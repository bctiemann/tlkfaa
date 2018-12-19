from django.contrib import admin
from fanart import models as fanart_models
from pms import models as pms_models
from django_extensions.admin import ForeignKeyAutocompleteAdmin

import logging
logger = logging.getLogger(__name__)


class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'date_sent', 'message',)
    list_filter = ()
    readonly_fields = ('sender', 'recipient',)
    user_id_for_formfield = None
admin.site.register(pms_models.PrivateMessage, PrivateMessageAdmin)

