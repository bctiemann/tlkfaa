from django.contrib import admin
from fanart import models as fanart_models

import logging
logger = logging.getLogger(__name__)


class PictureCharacterInline(admin.TabularInline):
    model = fanart_models.PictureCharacter
    extra = 1


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'num_pictures', 'date_joined',)
    search_fields = ('username', 'email',)
    readonly_fields = ()
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
    readonly_fields = ('artist', 'approved_by',)
#    inlines = (PictureCharacterInline,)
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
    readonly_fields = ('user',)
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
    readonly_fields = ('user', 'picture', 'reply_to',)
    user_id_for_formfield = None
admin.site.register(fanart_models.PictureComment, PictureCommentAdmin)


class ShoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'date_posted',)
    list_filter = ()
    readonly_fields = ('user', 'artist',)
    user_id_for_formfield = None
admin.site.register(fanart_models.Shout, ShoutAdmin)


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'owner', 'date_created',)
    list_filter = ()
    readonly_fields = ('creator', 'owner', 'adopted_from', 'profile_picture', 'profile_coloring_picture',)
    user_id_for_formfield = None
admin.site.register(fanart_models.Character, CharacterAdmin)


#class ColoringBaseAdmin(admin.ModelAdmin):
#    list_display = ('creator', 'date_posted',)
#    list_filter = ()
#    readonly_fields = ('creator', 'picture',)
#    user_id_for_formfield = None
#admin.site.register(fanart_models.ColoringBase, ColoringBaseAdmin)

#class ColoringPictureAdmin(admin.ModelAdmin):
#    list_display = ('artist', 'date_posted',)
#    list_filter = ()
#    readonly_fields = ('artist', 'base',)
#    user_id_for_formfield = None
#admin.site.register(fanart_models.ColoringPicture, ColoringPictureAdmin)

#class TradingOfferAdmin(admin.ModelAdmin):
#    list_display = ('artist', 'date_posted',)
#    list_filter = ()
#    readonly_fields = ('artist', 'character', 'adopted_by',)
#    user_id_for_formfield = None
#admin.site.register(fanart_models.TradingOffer, TradingOfferAdmin)


#class TradingClaimAdmin(admin.ModelAdmin):
#    list_display = ('user', 'date_posted', 'date_fulfilled',)
#    list_filter = ()
#    readonly_fields = ('user', 'offer',)
#    user_id_for_formfield = None
#admin.site.register(fanart_models.TradingClaim, TradingClaimAdmin)


class GiftPictureAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'picture', 'date_accepted',)
    list_filter = ()
    readonly_fields = ('sender', 'recipient', 'picture',)
    user_id_for_formfield = None
admin.site.register(fanart_models.GiftPicture, GiftPictureAdmin)


class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ()
    readonly_fields = ()
    user_id_for_formfield = None
admin.site.register(fanart_models.SocialMedia, SocialMediaAdmin)


class SocialMediaIdentityAdmin(admin.ModelAdmin):
    list_display = ('user', 'social_media', 'identity',)
    list_filter = ()
    readonly_fields = ('user',)
    user_id_for_formfield = None
admin.site.register(fanart_models.SocialMediaIdentity, SocialMediaIdentityAdmin)


class ContestAdmin(admin.ModelAdmin):
    list_display = ('creator', 'title', 'type', 'date_end',)
    list_filter = ('type',)
    readonly_fields = ('creator',)
    user_id_for_formfield = None
admin.site.register(fanart_models.Contest, ContestAdmin)


class ContestEntryAdmin(admin.ModelAdmin):
    list_display = ('contest', 'picture', 'date_entered', 'num_votes',)
    list_filter = ('contest',)
    readonly_fields = ('picture',)
    user_id_for_formfield = None
admin.site.register(fanart_models.ContestEntry, ContestEntryAdmin)


class BulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date_posted', 'is_published', 'is_admin',)
    list_filter = ('is_admin',)
    readonly_fields = ('user',)
    user_id_for_formfield = None
admin.site.register(fanart_models.Bulletin, BulletinAdmin)


class ShowcaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'is_visible',)
admin.site.register(fanart_models.Showcase, ShowcaseAdmin)


class FeaturedArtistAdmin(admin.ModelAdmin):
    list_display = ('artist', 'month_featured',)
    readonly_fields = ('artist',)
admin.site.register(fanart_models.FeaturedArtist, FeaturedArtistAdmin)

class FeaturedArtistPictureAdmin(admin.ModelAdmin):
    list_display = ('featured_artist', 'picture',)
#    readonly_fields = ('featured_artist',)
admin.site.register(fanart_models.FeaturedArtistPicture, FeaturedArtistPictureAdmin)

