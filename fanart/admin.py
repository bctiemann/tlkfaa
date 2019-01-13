from django.contrib import admin
from fanart import models as fanart_models
from django_extensions.admin import ForeignKeyAutocompleteAdmin

import logging
logger = logging.getLogger(__name__)


class PictureCharacterInline(admin.TabularInline):
    model = fanart_models.PictureCharacter
    extra = 1


#class UserAdmin(admin.ModelAdmin):
class UserAdmin(ForeignKeyAutocompleteAdmin):
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


#class PictureAdmin(admin.ModelAdmin):
class PictureAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('filename', 'artist', 'date_uploaded',)
    list_filter = ()
    readonly_fields = ('tags',)
#    readonly_fields = ('artist', 'approved_by', 'tags')
    related_search_fields = {
        'artist': ('username',),
        'approved_by': ('username',),
        'tags': ('tag'),
    }
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

#    def get_related_filter(self, model, request):
#        print 'foobar'
#        logger.info('fooobar')
#        return None

admin.site.register(fanart_models.Picture, PictureAdmin)


class PendingAdmin(admin.ModelAdmin):
    list_display = ('filename', 'artist', 'date_uploaded',)
    list_filter = ()
    readonly_fields = ('artist', 'approved_by',)
#    inlines = (PictureCharacterInline,)
    artist_id_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.artist_id_for_formfield = obj.artist_id
        return super(PendingAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'folder':
            kwargs['queryset'] = fanart_models.Folder.objects.filter(user=self.artist_id_for_formfield)
        if db_field.name == 'replaces_picture':
            kwargs['queryset'] = fanart_models.Picture.objects.filter(artist=self.artist_id_for_formfield)
        return super(PendingAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(fanart_models.Pending, PendingAdmin)


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


class ThreadedCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'picture', 'date_posted', 'num_replies',)
    list_filter = ()
    readonly_fields = ('user', 'picture', 'reply_to',)
    user_id_for_formfield = None
admin.site.register(fanart_models.ThreadedComment, ThreadedCommentAdmin)


class ShoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'date_posted',)
    list_filter = ()
    readonly_fields = ('user', 'artist',)
    user_id_for_formfield = None
admin.site.register(fanart_models.Shout, ShoutAdmin)


#class BulletinCommentAdmin(admin.ModelAdmin):
#    list_display = ('user', 'bulletin', 'date_posted', 'num_replies',)
#    list_filter = ()
#    readonly_fields = ('user', 'bulletin', 'reply_to',)
#    user_id_for_formfield = None
#admin.site.register(fanart_models.BulletinComment, BulletinCommentAdmin)


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'owner', 'date_created',)
    list_filter = ()
    search_fields = ('name', 'owner__username')
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


class SocialMediaIdentityAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('user', 'social_media', 'identity',)
    list_filter = ()
    related_search_fields = {
        'user': ('username', 'email',),
    }

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


#class FeaturedArtistAdmin(admin.ModelAdmin):
class FeaturedArtistAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('artist', 'month_featured',)
#    readonly_fields = ('artist',)
    related_search_fields = {
        'artist': ('username',),
    }
admin.site.register(fanart_models.FeaturedArtist, FeaturedArtistAdmin)

#class FeaturedArtistPictureAdmin(admin.ModelAdmin):
class FeaturedArtistPictureAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('featured_artist', 'picture',)
#    readonly_fields = ('featured_artist', 'picture',)
    related_search_fields = {
        'featured_artist': ('artist__username',),
        'picture': ('filename',),
    }

#    def get_form(self, request, obj=None, **kwargs):
#        if obj:
#            self.user_id_for_formfield = obj.featured_artist.artist_id
#        return super(FeaturedArtistPictureAdmin, self).get_form(request, obj, **kwargs)

#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == 'picture':
#            kwargs['queryset'] = fanart_models.Picture.objects.filter(artist=self.user_id_for_formfield)
#        return super(FeaturedArtistPictureAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(fanart_models.FeaturedArtistPicture, FeaturedArtistPictureAdmin)

class RevisionLogAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'entry',)
admin.site.register(fanart_models.RevisionLog, RevisionLogAdmin)

class ModNoteAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('date_created', 'artist', 'moderator',)
    related_search_fields = {
        'artist': ('username',),
        'moderator': ('username',),
    }
admin.site.register(fanart_models.ModNote, ModNoteAdmin)

