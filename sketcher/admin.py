# -*- coding: utf-8 -*-


from django.contrib import admin
from sketcher.models import Drawpile


class DrawpileAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'admin_url', 'last_checked_at', 'is_running',)


admin.site.register(Drawpile, DrawpileAdmin)
