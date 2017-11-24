from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from django.contrib.auth import views as auth_views
from fanart import views as fanart_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(
        r'^login/$',
        fanart_views.LoginView.as_view(),
        name='login',
    ),
    url(r'^logout/', auth_views.logout, {'next_page': 'home'}, name='logout'),

    url(r'^$', fanart_views.HomeView.as_view(), name='home'),
    url(r'^Artists/(?:(?P<list>[a-z]+)/)?$', fanart_views.ArtistsView.as_view(), name='artists'),
    url(r'^Artwork/(?:(?P<list>[a-z]+)/)?$', fanart_views.ArtworkView.as_view(), name='artwork'),
#    url(r'^Characters/(?:(?P<character_id>[0-9]+)/)?$', fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^Characters/(?:(?P<mode>[a-z]+)/)?$', fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^TradingTree/(?:(?P<offer_type>(icon|adoptable))/)?$', fanart_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^ColoringCave/(?:(?P<coloring_base_id>[0-9]+)/)?$', fanart_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^Special/(?:(?P<special_id>[0-9]+)/)?$', fanart_views.SpecialFeaturesView.as_view(), name='special'),
    url(r'^Contests/(?:(?P<contest_type>(global|personal))/)?$', fanart_views.ContestsView.as_view(), name='contests'),
    url(r'^FavoritePictures/$', fanart_views.FavoritePicturesView.as_view(), name='favorite-pictures'),

    url(r'^Guidelines/$', fanart_views.GuidelinesView.as_view(), name='guidelines'),

    url(r'^userbox/set/(?P<box>[a-z_]+)/(?P<show>[01]+)$', fanart_views.UserBoxSetView.as_view(), name='userbox-set'),
    url(r'^userbox/favorite_artists_box/$', fanart_views.FavoriteArtistsBoxView.as_view(), name='favorite-artists-box'),
    url(r'^userbox/favorite_pictures_box/$', fanart_views.FavoritePicturesBoxView.as_view(), name='favorite-pictures-box'),
    url(r'^userbox/sketcher_box/$', fanart_views.SketcherBoxView.as_view(), name='sketcher-box'),
    url(r'^userbox/community_art_box/$', fanart_views.CommunityArtBoxView.as_view(), name='community-art-box'),
    url(r'^userbox/contests_box/$', fanart_views.ContestsBoxView.as_view(), name='contests-box'),
    url(r'^userbox/tool_box/$', fanart_views.ToolBoxView.as_view(), name='tool-box'),

#    url(r'^Artwork/Artists/(?P<dir_name>[^/]+)/(?:(?P<subview>[a-z]+)/)?$', fanart_views.ArtistView.as_view(), name='artist'),
    url(r'^Artists/(?P<dir_name>[^/]+)/$', fanart_views.ArtistView.as_view(), name='artist'),
    url(r'^Artists/(?P<dir_name>[^/]+)/Gallery/(?:(?P<subview>[a-z]+)/)?$', fanart_views.ArtistGalleryView.as_view(), name='artist-gallery'),
    url(r'^Artists/(?P<dir_name>[^/]+)/ArtWall/$', fanart_views.ArtWallView.as_view(), name='artist-artwall'),
    url(r'^Artists/(?P<dir_name>[^/]+)/Characters/$', fanart_views.CharactersView.as_view(), name='artist-characters'),

    url(r'^picture/(?P<picture_id>[0-9]+)/$', fanart_views.PictureView.as_view(), name='picture'),
    url(r'^character/(?P<character_id>[0-9]+)/$', fanart_views.CharacterView.as_view(), name='character'),
    url(r'^contest/(?P<contest_id>[0-9]+)/$', fanart_views.ContestView.as_view(), name='contest'),
    url(r'^contest/(?P<contest_id>[0-9]+)/entry/create/$', fanart_views.ContestEntryCreateView.as_view(), name='contest-entry-create'),
    url(r'^contest/entry/(?P<entry_id>[0-9]+)/delete/$', fanart_views.ContestEntryDeleteView.as_view(), name='contest-entry-delete'),
    url(r'^contest/(?P<contest_id>[0-9]+)/vote/$', fanart_views.ContestVoteView.as_view(), name='contest-vote'),

    url(r'^comments/(?P<picture_id>[0-9]+)/$', fanart_views.CommentsView.as_view(), name='comments'),
    url(r'^comments/(?P<picture_id>[0-9]+)/reply/$', fanart_views.PostCommentView.as_view(), name='post-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/detail/$', fanart_views.CommentDetailView.as_view(), name='comment-detail'),
    url(r'^comment/(?P<comment_id>[0-9]+)/edit/$', fanart_views.EditCommentView.as_view(), name='edit-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/delete/$', fanart_views.DeleteCommentView.as_view(), name='delete-comment'),

    url(r'^shouts/(?P<artist_id>[0-9]+)/$', fanart_views.ShoutsView.as_view(), name='shouts'),
    url(r'^shouts/(?P<artist_id>[0-9]+)/post/$', fanart_views.PostShoutView.as_view(), name='post-shout'),
    url(r'^shout/(?P<shout_id>[0-9]+)/delete/$', fanart_views.DeleteShoutView.as_view(), name='delete-shout'),

    url(r'^comments/mark_read/$', fanart_views.MarkCommentsReadView.as_view(), name='mark-comments-read'),
    url(r'^shouts/mark_read/$', fanart_views.MarkShoutsReadView.as_view(), name='mark-shouts-read'),

    url(r'^folders/(?P<artist_id>[0-9]+)/$', fanart_views.FoldersView.as_view(), name='folders'),
    url(r'^artists/(?P<list>[a-z]+)/$', fanart_views.ArtistsListView.as_view(), name='artists-list'),
    url(r'^artwork/(?P<list>[a-z]+)/$', fanart_views.ArtworkListView.as_view(), name='artwork-list'),

    url(r'^characters-ac/(?P<term>.+)/$', fanart_views.CharactersAutocompleteView.as_view(), name='characters-autocomplete'),
    url(r'^species-ac/(?P<term>.+)/$', fanart_views.SpeciesAutocompleteView.as_view(), name='species-autocomplete'),
    url(r'^artists-ac/(?P<term>.+)/$', fanart_views.ArtistsAutocompleteView.as_view(), name='artists-autocomplete'),
    url(r'^check-name/$', fanart_views.CheckNameView.as_view(), name='check-name'),

    url(r'^offer/(?P<offer_id>[0-9]+)/$', fanart_views.OfferView.as_view(), name='offer'),
    url(r'^offer/(?P<offer_id>[0-9]+)/edit/$', fanart_views.EditOfferView.as_view(), name='edit-offer'),
    url(r'^offer/(?P<offer_id>[0-9]+)/status/$', fanart_views.OfferStatusView.as_view(), name='offer-status'),
    url(r'^claim/post/$', fanart_views.PostClaimView.as_view(), name='post-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/upload/$', fanart_views.UploadClaimView.as_view(), name='upload-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/upload/remove/$', fanart_views.RemoveUploadClaimView.as_view(), name='remove-upload-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/accept/$', fanart_views.AcceptClaimView.as_view(), name='accept-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/choose/$', fanart_views.ChooseAdopterView.as_view(), name='choose-adopter'),
    url(r'^claim/(?P<claim_id>[0-9]+)/remove/$', fanart_views.RemoveClaimView.as_view(), name='remove-claim'),

    url(r'^coloring/(?P<coloring_base_id>[0-9]+)/$', fanart_views.ColoringPicturesView.as_view(), name='coloring-pictures'),
    url(r'^coloring/(?P<coloring_base_id>[0-9]+)/upload/$', fanart_views.UploadColoringPictureView.as_view(), name='upload-coloring-picture'),
    url(r'^coloring/(?P<coloring_base_id>[0-9]+)/status/$', fanart_views.ColoringPictureStatusView.as_view(), name='coloring-picture-status'),
    url(r'^coloring/(?P<coloring_picture_id>[0-9]+)/remove/$', fanart_views.RemoveColoringPictureView.as_view(), name='remove-coloring-picture'),

#    url(r'^upload/$', fanart_views.UploadPictureView.as_view(), name='upload-picture'),

    url(r'^fave/(?P<fave_type>[a-z]+)/(?P<object_id>[0-9]+)/$', fanart_views.ToggleFaveView.as_view(), name='toggle-fave'),
    url(r'^block/(?P<user_id>[0-9]+)/$', fanart_views.ToggleBlockView.as_view(), name='toggle-block'),

    url(r'^tooltip/picture/(?P<picture_id>[0-9]+)/$', fanart_views.PictureTooltipView.as_view(), name='picture-tooltip'),
    url(r'^tooltip/coloring_picture/(?P<coloring_picture_id>[0-9]+)/$', fanart_views.ColoringPictureTooltipView.as_view(), name='coloring-picture-tooltip'),

    url(r'^pick/picture/(?:(?P<target>[a-z]+)/)?$', fanart_views.PicturePickerView.as_view(), name='picture-picker'),

    url(r'^pms/(?P<box>(in|out|trash))/$', fanart_views.PMsView.as_view(), name='pms'),
    url(r'^pms/(?P<action>(delete|restore))/$', fanart_views.PMsMoveView.as_view(), name='pms-move'),
    url(r'^pm/(?:(?P<pm_id>[0-9]+)/)?$', fanart_views.PMView.as_view(), name='pm'),
    url(r'^pm/shout/(?P<shout_id>[0-9]+)/?$', fanart_views.PMShoutView.as_view(), name='pm-shout'),
    url(r'^pm/user/(?:(?P<recipient_id>[0-9]+)/)?$', fanart_views.PMUserView.as_view(), name='pm-user'),
    url(r'^pm/create/$', fanart_views.PMCreateView.as_view(), name='pm-create'),
    url(r'^pm/success/(?P<pm_id>[0-9]+)/$', fanart_views.PMSuccessView.as_view(), name='pm-success'),

    url(r'^admin_announcements/(?P<count>[0-9]+)/(?P<start>[0-9]+)/$', fanart_views.AdminAnnouncementsView.as_view(), name='admin-announcements'),
    url(r'^bulletins/(?P<count>[0-9]+)/(?P<start>[0-9]+)/$', fanart_views.BulletinsView.as_view(), name='admin-announcements'),

    url(r'^social_media/identities/$', fanart_views.SocialMediaIdentitiesView.as_view(), name='social-media-identities'),
    url(r'^social_media/add/$', fanart_views.AddSocialMediaIdentityView.as_view(), name='add-social-media-identity'),
    url(r'^social_media/(?P<identity_id>[0-9]+)/remove/$', fanart_views.RemoveSocialMediaIdentityView.as_view(), name='remove-social-media-identity'),

    url(r'^profile-pic/upload/$', fanart_views.UploadProfilePicView.as_view(), name='upload-profile-pic'),
    url(r'^profile-pic/upload/status/$', fanart_views.ProfilePicStatusView.as_view(), name='profile-pic-status'),
    url(r'^profile-pic/remove/$', fanart_views.RemoveProfilePicView.as_view(), name='remove-profile-pic'),

    url(r'^ArtManager/', include('artmanager.urls', 'artmanager')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
