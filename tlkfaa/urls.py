from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from fanart import views as fanart_views
from fanart.models import artists_tabs, artwork_tabs
from fanart.views import approval as approval_views
from trading_tree import views as trading_tree_views
from coloring_cave import views as coloring_cave_views
from pms import views as pms_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^admin/approve.jsp$', RedirectView.as_view(url='/admin/approve/', permanent=True), name='approve-redirect'),
    url(r'^admin/approve/$', approval_views.ApprovalHomeView.as_view(), name='approve'),
    url(r'^admin/approve/list/$', approval_views.PendingListView.as_view(), name='pending-list'),
    url(r'^admin/approve/count/$', approval_views.PendingCountView.as_view(), name='pending-count'),
    url(r'^admin/approve/(?P<pending_id>[0-9]+)/$', approval_views.PendingDetailView.as_view(), name='pending-detail'),
    url(r'^admin/approve/(?P<pending_id>[0-9]+)/approve/$', approval_views.PendingApproveView.as_view(), name='pending-approve'),
    url(r'^admin/approve/(?P<pending_id>[0-9]+)/reject/$', approval_views.PendingRejectView.as_view(), name='pending-reject'),
    url(r'^admin/approve/(?P<pending_id>[0-9]+)/resize/$', approval_views.PendingResizeView.as_view(), name='pending-resize'),
    url(r'^admin/approve/(?P<pending_id>[0-9]+)/convert/$', approval_views.PendingConvertView.as_view(), name='pending-convert'),
    url(r'^admin/approve/(?P<pending_id>[0-9]+)/upload_thumb/$', approval_views.PendingUploadThumbView.as_view(), name='pending-upload-thumb'),
#    url(r'^admin/approve/thumb_status/$', approval_views.PendingThumbStatusView.as_view(), name='pending-thumb-status'),
    url(r'^admin/approve/auto_approval/(?P<artist_id>[0-9]+)/$', approval_views.AutoApprovalView.as_view(), name='pending-auto-approval'),
    url(r'^admin/approve/mod_notes/(?P<artist_id>[0-9]+)/$', approval_views.ModNotesView.as_view(), name='pending-mod-notes'),
    url(r'^admin/approve/mod_notes/(?P<artist_id>[0-9]+)/add/$', approval_views.AddModNoteView.as_view(), name='pending-mod-notes-add'),

    url(
        r'^login/$',
        fanart_views.LoginView.as_view(),
        name='login',
    ),
    url(r'^logout/', auth_views.logout, {'next_page': 'home'}, name='logout'),

    url(r'^$', fanart_views.HomeView.as_view(), name='home'),
    url(r'^Artists/(?:(?P<list>({0}))/)?$'.format('|'.join(artists_tabs)), fanart_views.ArtistsView.as_view(), name='artists'),
    url(r'^Artwork/(?:(?P<list>({0}))/)?$'.format('|'.join(artwork_tabs)), fanart_views.ArtworkView.as_view(), name='artwork'),
#    url(r'^Characters/(?:(?P<character_id>[0-9]+)/)?$', fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^Characters/(?:(?P<mode>[a-z]+)/)?$', fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^TradingTree/(?:(?P<offer_type>(icon|adoptable))/)?$', trading_tree_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^ColoringCave/(?:(?P<coloring_base_id>[0-9]+)/)?$', coloring_cave_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^ColoringCave/artist/(?P<dir_name>[^/]+)?$', fanart_views.ColoringPicturesView.as_view(), name='coloring-cave-artist'),
    url(r'^Showcase/(?:(?P<showcase_id>[0-9]+)/)?$', fanart_views.ShowcasesView.as_view(), name='showcases'),
    url(r'^Contests/(?:(?P<contest_type>(global|personal))/)?$', fanart_views.ContestsView.as_view(), name='contests'),
    url(r'^FavoritePictures/$', fanart_views.FavoritePicturesView.as_view(), name='favorite-pictures'),
    url(r'^Featured/(?:(?P<month_featured>[0-9]{4}-[0-9]{2})/)?$', fanart_views.FeaturedArtistsView.as_view(), name='featured-artists'),

    url(r'^about/$', fanart_views.AboutView.as_view(), name='about'),
    url(r'^tos/$', fanart_views.TermsOfServiceView.as_view(), name='tos'),
    url(r'^privacy/$', fanart_views.PrivacyView.as_view(), name='privacy'),
    url(r'^help/$', fanart_views.HelpView.as_view(), name='help'),

    url(r'^Register/$', fanart_views.RegisterView.as_view(), name='register'),
    url(r'^Recovery/$', fanart_views.RecoveryView.as_view(), name='recovery'),
    url(r'^Recovery/reset/$', fanart_views.UsernameAwarePasswordResetView.as_view(), name='recovery-reset'),
    url(r'^password_reset/done/$', fanart_views.PasswordResetDoneView.as_view(template_name='fanart/recovery_done.html'), name='password_reset_done'),
    url(r'^Recovery/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', fanart_views.HashedPasswordResetConfirmView.as_view(template_name='fanart/recovery_reset.html', post_reset_login=True), name='password_reset_confirm'),
    url(r'^Recovery/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(template_name='fanart/recovery_complete.html'), name='password_reset_complete'),

    url(r'^ApproveRequest/(?P<hash>[0-9a-f-]+)/$', fanart_views.ApproveRequestView.as_view(), name='approve-request'),
    url(r'^ApproveRequest/(?P<hash>[0-9a-f-]+)/success/$', fanart_views.ApproveRequestSuccessView.as_view(), name='approve-request-success'),

    url(r'^Guidelines/$', fanart_views.GuidelinesView.as_view(), name='guidelines'),

    url(r'^random_popular/$', fanart_views.RandomPopularView.as_view(), name='random-popular'),
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

    url(r'^Artwork/offers/(?P<offer_id>[0-9]+)\.(?P<ext>[a-z]+)$', trading_tree_views.OfferRedirectView.as_view(), name='offer-redirect'),
    url(r'^Picture.jsp$', fanart_views.PictureRedirectByIDView.as_view(), name='picture-redirect'),
    url(r'^Artists/(?P<dir_name>[^/]+)/(?P<filename>[^/]+)$', fanart_views.PictureRedirectByPathView.as_view(), name='picture-redirect'),

    url(r'^picture/(?P<picture_id>[0-9]+)/$', fanart_views.PictureView.as_view(), name='picture'),
    url(r'^picture/(?P<picture_id>[0-9]+)/fans/$', fanart_views.PictureFansView.as_view(), name='picture-fans'),
    url(r'^character/(?P<character_id>[0-9]+)/$', fanart_views.CharacterView.as_view(), name='character'),
    url(r'^contest/(?P<contest_id>[0-9]+)/$', fanart_views.ContestView.as_view(), name='contest'),
    url(r'^contest/(?P<contest_id>[0-9]+)/entry/create/$', fanart_views.ContestEntryCreateView.as_view(), name='contest-entry-create'),
    url(r'^contest/entry/(?P<entry_id>[0-9]+)/delete/$', fanart_views.ContestEntryDeleteView.as_view(), name='contest-entry-delete'),
    url(r'^contest/(?P<contest_id>[0-9]+)/vote/$', fanart_views.ContestVoteView.as_view(), name='contest-vote'),
    url(r'^contest/setup/$', fanart_views.ContestSetupView.as_view(), name='contest-setup'),
    url(r'^contest/setup/success/$', fanart_views.ContestSetupSuccessView.as_view(), name='contest-setup-success'),

    url(r'^comments/(?P<picture_id>[0-9]+)/$', fanart_views.CommentsView.as_view(), name='comments'),
    url(r'^comments/(?P<picture_id>[0-9]+)/reply/$', fanart_views.PostCommentView.as_view(), name='post-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/detail/$', fanart_views.CommentDetailView.as_view(), name='comment-detail'),
    url(r'^comment/(?P<comment_id>[0-9]+)/edit/$', fanart_views.EditCommentView.as_view(), name='edit-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/delete/$', fanart_views.DeleteCommentView.as_view(), name='delete-comment'),

    url(r'^shouts/(?P<artist_id>[0-9]+)/$', fanart_views.ShoutsView.as_view(), name='shouts'),
    url(r'^shouts/(?P<artist_id>[0-9]+)/post/$', fanart_views.PostShoutView.as_view(), name='post-shout'),
    url(r'^shout/(?P<shout_id>[0-9]+)/delete/$', fanart_views.DeleteShoutView.as_view(), name='delete-shout'),

#    url(r'^comments/mark_read/$', fanart_views.MarkCommentsReadView.as_view(), name='mark-comments-read'),
#    url(r'^shouts/mark_read/$', fanart_views.MarkShoutsReadView.as_view(), name='mark-shouts-read'),

    url(r'^folders/(?P<artist_id>[0-9]+)/$', fanart_views.FoldersView.as_view(), name='folders'),
    url(r'^artists/(?P<list>[a-z]+)/$', fanart_views.ArtistsListView.as_view(), name='artists-list'),
    url(r'^artwork/(?P<list>[a-z]+)/$', fanart_views.ArtworkListView.as_view(), name='artwork-list'),

    url(r'^characters-ac/(?P<term>.+)/$', fanart_views.CharactersAutocompleteView.as_view(), name='characters-autocomplete'),
    url(r'^species-ac/(?P<term>.+)/$', fanart_views.SpeciesAutocompleteView.as_view(), name='species-autocomplete'),
    url(r'^artists-ac/(?P<term>.+)/$', fanart_views.ArtistsAutocompleteView.as_view(), name='artists-autocomplete'),
    url(r'^check-name/(?P<username>.+)/$', fanart_views.CheckNameAvailabilityView.as_view(), name='check-name'),

    url(r'^offer/(?P<offer_id>[0-9]+)/$', trading_tree_views.OfferView.as_view(), name='offer'),
    url(r'^offer/(?P<offer_id>[0-9]+)/edit/$', trading_tree_views.EditOfferView.as_view(), name='edit-offer'),
    url(r'^offer/(?P<offer_id>[0-9]+)/remove/$', trading_tree_views.RemoveOfferView.as_view(), name='remove-offer'),
    url(r'^offer/(?P<offer_id>[0-9]+)/status/$', trading_tree_views.OfferStatusView.as_view(), name='offer-status'),
    url(r'^claim/post/$', trading_tree_views.PostClaimView.as_view(), name='post-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/upload/$', trading_tree_views.UploadClaimView.as_view(), name='upload-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/upload/remove/$', trading_tree_views.RemoveClaimUploadView.as_view(), name='remove-claim-upload'),
    url(r'^claim/(?P<claim_id>[0-9]+)/accept/$', trading_tree_views.AcceptClaimView.as_view(), name='accept-claim'),
    url(r'^claim/(?P<claim_id>[0-9]+)/choose/$', trading_tree_views.ChooseAdopterView.as_view(), name='choose-adopter'),
    url(r'^claim/(?P<claim_id>[0-9]+)/remove/$', trading_tree_views.RemoveClaimView.as_view(), name='remove-claim'),

    url(r'^coloring/(?P<coloring_base_id>[0-9]+)/$', coloring_cave_views.ColoringPicturesView.as_view(), name='coloring-pictures'),
    url(r'^coloring/(?P<coloring_base_id>[0-9]+)/upload/$', coloring_cave_views.UploadColoringPictureView.as_view(), name='upload-coloring-picture'),
    url(r'^coloring/(?P<coloring_base_id>[0-9]+)/status/$', coloring_cave_views.ColoringPictureStatusView.as_view(), name='coloring-picture-status'),
    url(r'^coloring/(?P<coloring_picture_id>[0-9]+)/remove/$', coloring_cave_views.RemoveColoringPictureView.as_view(), name='remove-coloring-picture'),

#    url(r'^upload/$', fanart_views.UploadPictureView.as_view(), name='upload-picture'),

    url(r'^fave/(?P<fave_type>[a-z]+)/(?P<object_id>[0-9]+)/$', fanart_views.ToggleFaveView.as_view(), name='toggle-fave'),
    url(r'^visible/(?P<artist_id>[0-9]+)/$', fanart_views.ToggleVisibleView.as_view(), name='toggle-visible'),
    url(r'^block/(?P<user_id>[0-9]+)/$', fanart_views.ToggleBlockView.as_view(), name='toggle-block'),

    url(r'^tooltip/picture/(?P<picture_id>[0-9]+)/$', fanart_views.PictureTooltipView.as_view(), name='picture-tooltip'),
    url(r'^tooltip/coloring_picture/(?P<coloring_picture_id>[0-9]+)/$', fanart_views.ColoringPictureTooltipView.as_view(), name='coloring-picture-tooltip'),
    url(r'^tooltip/character/(?P<character_id>[0-9]+)/$', fanart_views.CharacterTooltipView.as_view(), name='character-tooltip'),
    url(r'^tooltip/msg/(?P<msg_id>[0-9]+)/$', fanart_views.MessageTooltipView.as_view(), name='message-tooltip'),

    url(r'^pick/picture/(?:(?P<target>[a-z_-]+)/)?$', fanart_views.PicturePickerView.as_view(), name='picture-picker'),
    url(r'^pick/character/(?:(?P<target>[a-z_-]+)/)?$', fanart_views.CharacterPickerView.as_view(), name='character-picker'),

    url(r'^pms/(?P<box>(in|out|trash))/$', pms_views.PMsView.as_view(), name='pms'),
    url(r'^pms/(?P<action>(delete|restore))/$', pms_views.PMsMoveView.as_view(), name='pms-move'),
    url(r'^pm/(?:(?P<pm_id>[0-9]+)/)?$', pms_views.PMView.as_view(), name='pm'),
    url(r'^pm/shout/(?P<shout_id>[0-9]+)/?$', pms_views.PMShoutView.as_view(), name='pm-shout'),
    url(r'^pm/user/(?:(?P<recipient_id>[0-9]+)/)?$', pms_views.PMUserView.as_view(), name='pm-user'),
    url(r'^pm/create/$', pms_views.PMCreateView.as_view(), name='pm-create'),
    url(r'^pm/success/(?P<pm_id>[0-9]+)/$', pms_views.PMSuccessView.as_view(), name='pm-success'),

    url(r'^admin_announcements/(?P<count>[0-9]+)/(?P<start>[0-9]+)/$', fanart_views.AdminAnnouncementsView.as_view(), name='admin-announcements'),
    url(r'^bulletins/(?P<count>[0-9]+)/(?P<start>[0-9]+)/$', fanart_views.BulletinsView.as_view(), name='bulletins'),
    url(r'^bulletin/(?P<bulletin_id>[0-9]+)/$', fanart_views.BulletinView.as_view(), name='bulletin'),

    url(r'^aotm/vote/$', fanart_views.AotmVoteView.as_view(), name='aotm-vote'),
    url(r'^aotm/vote/form/$', fanart_views.AotmVoteFormView.as_view(), name='aotm-vote-form'),

    url(r'^social_media/identities/$', fanart_views.SocialMediaIdentitiesView.as_view(), name='social-media-identities'),
    url(r'^social_media/add/$', fanart_views.AddSocialMediaIdentityView.as_view(), name='add-social-media-identity'),
    url(r'^social_media/(?P<identity_id>[0-9]+)/remove/$', fanart_views.RemoveSocialMediaIdentityView.as_view(), name='remove-social-media-identity'),

    url(r'^profile-pic/upload/$', fanart_views.UploadProfilePicView.as_view(), name='upload-profile-pic'),
    url(r'^profile-pic/upload/status/$', fanart_views.ProfilePicStatusView.as_view(), name='profile-pic-status'),
    url(r'^profile-pic/remove/$', fanart_views.RemoveProfilePicView.as_view(), name='remove-profile-pic'),

    url(r'^banner/upload/$', fanart_views.UploadBannerView.as_view(), name='upload-banner'),
    url(r'^banner/upload/status/$', fanart_views.BannerStatusView.as_view(), name='banner-status'),
    url(r'^banner/remove/$', fanart_views.RemoveBannerView.as_view(), name='remove-banner'),

    url(r'^ArtManager/', include('artmanager.urls', 'artmanager')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
