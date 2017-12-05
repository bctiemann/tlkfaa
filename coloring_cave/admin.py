from django.contrib import admin
from fanart import models as fanart_models
from coloring_cave import models as coloring_cave_models

import logging
logger = logging.getLogger(__name__)


class BaseAdmin(admin.ModelAdmin):
    list_display = ('creator', 'date_posted',)
    list_filter = ()
    readonly_fields = ('creator', 'picture',)
    user_id_for_formfield = None
admin.site.register(coloring_cave_models.Base, BaseAdmin)

class ColoringPictureAdmin(admin.ModelAdmin):
    list_display = ('artist', 'date_posted',)
    list_filter = ()
    readonly_fields = ('artist', 'base',)
    user_id_for_formfield = None
admin.site.register(coloring_cave_models.ColoringPicture, ColoringPictureAdmin)

