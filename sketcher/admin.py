# -*- coding: utf-8 -*-


from django.contrib import admin
from sketcher.models import Drawpile, SketcherAccessToken


class DrawpileAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'admin_url', 'last_checked_at', 'is_running',)


class SketcherAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'used_at',)
    list_filter = ('used_at',)
    raw_id_fields = ('user',)


admin.site.register(Drawpile, DrawpileAdmin)
admin.site.register(SketcherAccessToken, SketcherAccessTokenAdmin)
