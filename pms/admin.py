from django.contrib import admin
from fanart import models as fanart_models
from pms import models as pms_models

import logging
logger = logging.getLogger(__name__)


class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'date_sent', 'message',)
    list_filter = ()
    autocomplete_fields = ('reply_to', 'root_pm',)
    search_fields = ('subject',)
    readonly_fields = ('sender', 'recipient',)
    user_id_for_formfield = None
admin.site.register(pms_models.PrivateMessage, PrivateMessageAdmin)

