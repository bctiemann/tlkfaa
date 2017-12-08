from django.contrib import admin
from fanart import models as fanart_models
from trading_tree import models as trading_tree_models

import logging
logger = logging.getLogger(__name__)


class OfferAdmin(admin.ModelAdmin):
    list_display = ('artist', 'date_posted',)
    list_filter = ()
    readonly_fields = ('artist', 'character', 'adopted_by',)
    user_id_for_formfield = None
admin.site.register(trading_tree_models.Offer, OfferAdmin)


class ClaimAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_posted', 'date_fulfilled',)
    list_filter = ()
    readonly_fields = ('user', 'offer',)
    user_id_for_formfield = None
admin.site.register(trading_tree_models.Claim, ClaimAdmin)
