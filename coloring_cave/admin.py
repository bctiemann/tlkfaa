from django.contrib import admin
from fanart import models

import logging
logger = logging.getLogger(__name__)


class ColoringBaseAdmin(admin.ModelAdmin):
    list_display = ('creator', 'date_posted',)
    list_filter = ()
    readonly_fields = ('creator', 'picture',)
    user_id_for_formfield = None
admin.site.register(models.ColoringBase, ColoringBaseAdmin)

class ColoringPictureAdmin(admin.ModelAdmin):
    list_display = ('artist', 'date_posted',)
    list_filter = ()
    readonly_fields = ('artist', 'base',)
    user_id_for_formfield = None
admin.site.register(models.ColoringPicture, ColoringPictureAdmin)
