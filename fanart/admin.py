from django.contrib import admin
from fanart import models as fanart_models

import logging
logger = logging.getLogger(__name__)


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'num_pictures', 'date_joined',)
    list_filter = ()
    readonly_fields=()
    user_id_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.user_id_for_formfield = obj.id
        return super(UserAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'sketcher_banned_by':
            kwargs['queryset'] = fanart_models.User.objects.filter(id=0)
        if db_field.name == 'example_pic':
            kwargs['queryset'] = fanart_models.Picture.objects.filter(artist=self.user_id_for_formfield)
        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(fanart_models.User, UserAdmin)


class PictureAdmin(admin.ModelAdmin):
    list_display = ('filename', 'artist', 'date_uploaded',)
    list_filter = ()
    readonly_fields=('artist', 'approved_by',)
    artist_id_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.artist_id_for_formfield = obj.artist_id
        return super(PictureAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'folder':
            kwargs['queryset'] = fanart_models.Folder.objects.filter(user=self.artist_id_for_formfield)
        return super(PictureAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(fanart_models.Picture, PictureAdmin)


class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user',)
    list_filter = ()
    readonly_fields=('user',)
    user_id_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.user_id_for_formfield = obj.user_id
        return super(FolderAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = fanart_models.Folder.objects.filter(user=self.user_id_for_formfield)
        if db_field.name == 'latest_picture':
            kwargs['queryset'] = fanart_models.Picture.objects.filter(artist=self.user_id_for_formfield)
        return super(FolderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(fanart_models.Folder, FolderAdmin)


class PictureCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'picture', 'date_posted', 'num_replies',)
    list_filter = ()
    readonly_fields=('user', 'picture', 'reply_to',)
    user_id_for_formfield = None
admin.site.register(fanart_models.PictureComment, PictureCommentAdmin)


class ShoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'date_posted')
    list_filter = ()
    readonly_fields=('user', 'artist',)
    user_id_for_formfield = None
admin.site.register(fanart_models.Shout, ShoutAdmin)
