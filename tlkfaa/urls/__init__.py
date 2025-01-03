# import debug_toolbar
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path, register_converter

from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from fanart import views as fanart_views
from fanart.views import artists as artists_views
from fanart.views import artwork as artwork_views
from fanart.views import characters as characters_views
from fanart.views import chamber_of_stars as stars_views
from fanart.views import contests
from fanart.models import artists_tabs, artwork_tabs, characters_tabs
from fanart.views import approval as approval_views
from trading_tree import views as trading_tree_views
from coloring_cave import views as coloring_cave_views
from pms import views as pms_views


class MonthPathConverter:
    regex = '[0-9]{4}-[0-9]{2}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return value


register_converter(MonthPathConverter, "month")


urlpatterns = [
    # url(r'^favicon\.ico$', fanart_views.favicon),
    # url(r'^robots\.txt$', fanart_views.robots),

    path('admin/approve.jsp', RedirectView.as_view(pattern_name='approve', permanent=True), name='approve-redirect'),
    path('admin/approve/', include('tlkfaa.urls.approvals')),

    url(r'^admin/', admin.site.urls),

    url(
        r'^login/$',
        fanart_views.LoginView.as_view(),
        name='login',
    ),
    url(r'^logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    url(r'^$', fanart_views.HomeView.as_view(), name='home'),
    # url(r'^Artists/(?:(?P<list>({0}))/)?$'.format('|'.join(artists_tabs)), fanart_views.ArtistsView.as_view(), name='artists'),
    # url(r'^Artwork/(?:(?P<list>({0}))/)?$'.format('|'.join(artwork_tabs)), fanart_views.ArtworkView.as_view(), name='artwork'),
#    url(r'^Characters/(?:(?P<character_id>[0-9]+)/)?$', fanart_views.CharactersView.as_view(), name='characters'),
#     url(r'^Characters/(?:(?P<list>({0}))/)?$'.format('|'.join(characters_tabs)), fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^TradingTree/(?:(?P<offer_type>(icon|adoptable))/)?$', trading_tree_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^ColoringCave/(?:(?P<coloring_base_id>[0-9]+)/)?$', coloring_cave_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^ColoringCave/artist/(?P<dir_name>[^/]+)?$', fanart_views.ColoringPicturesView.as_view(), name='coloring-cave-artist'),
    # url(r'^Showcase/(?:(?P<showcase_id>[0-9]+)/)?$', fanart_views.ShowcasesView.as_view(), name='showcases'),
    url(r'^FavoritePictures/$', fanart_views.FavoritePicturesView.as_view(), name='favorite-pictures'),
    # url(r'^FeaturedArtists/(?:(?P<month_featured>[0-9]{4}-[0-9]{2})/)?$', showcases_views.FeaturedArtistsView.as_view(), name='featured-artists'),
    # url(r'^FeaturedPictures/$', showcases_views.FeaturedPicturesView.as_view(), name='featured-pictures'),
    url(r'^revision_log/$', fanart_views.RevisionLogView.as_view(), name='revision-log'),

    url(r'^about/$', fanart_views.AboutView.as_view(), name='about'),
    url(r'^tos/$', fanart_views.TermsOfServiceView.as_view(), name='tos'),
    url(r'^privacy/$', fanart_views.PrivacyView.as_view(), name='privacy'),
    url(r'^help/$', fanart_views.HelpView.as_view(), name='help'),

    url(r'^Register/$', fanart_views.RegisterView.as_view(), name='register'),
    url(r'^Recovery/$', fanart_views.RecoveryView.as_view(), name='recovery'),
    url(r'^Recovery/reset/$', fanart_views.UsernameAwarePasswordResetView.as_view(), name='recovery-reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name='fanart/recovery_done.html'), name='password_reset_done'),
    url(r'^Recovery/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,6}-[0-9A-Za-z]{1,32})/$', fanart_views.HashedPasswordResetConfirmView.as_view(template_name='fanart/recovery_reset.html', post_reset_login=True), name='password_reset_confirm'),
    url(r'^Recovery/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(template_name='fanart/recovery_complete.html'), name='password_reset_complete'),

    url(r'^ApproveRequest/(?P<hash>[0-9a-f-]+)/$', fanart_views.ApproveRequestView.as_view(), name='approve-request'),
    url(r'^ApproveRequest/(?P<hash>[0-9a-f-]+)/success/$', fanart_views.ApproveRequestSuccessView.as_view(), name='approve-request-success'),

    url(r'^Guidelines/$', fanart_views.GuidelinesView.as_view(), name='guidelines'),

    url(r'^random_popular/$', fanart_views.RandomPopularView.as_view(), name='random-popular'),
    url(r'^userbox/set/$', fanart_views.UserBoxSetView.as_view(), name='userbox-set'),
    url(r'^userbox/favorite_artists_box/$', fanart_views.FavoriteArtistsBoxView.as_view(), name='favorite-artists-box'),
    url(r'^userbox/favorite_artists_box_with_counts/$', fanart_views.FavoriteArtistsBoxWithUnviewedCountsView.as_view(), name='favorite-artists-box-with-counts'),
    url(r'^userbox/favorite_pictures_box/$', fanart_views.FavoritePicturesBoxView.as_view(), name='favorite-pictures-box'),
    url(r'^userbox/sketcher_box/$', fanart_views.SketcherBoxView.as_view(), name='sketcher-box'),
    url(r'^userbox/community_art_box/$', fanart_views.CommunityArtBoxView.as_view(), name='community-art-box'),
    url(r'^userbox/contests_box/$', fanart_views.ContestsBoxView.as_view(), name='contests-box'),
    url(r'^userbox/tool_box/$', fanart_views.ToolBoxView.as_view(), name='tool-box'),

    path('Artists/', artists_views.ArtistsView.as_view(), name='artists'),
    path('Artists/name/<str:initial>/', artists_views.ArtistsByNameView.as_view(list_type='name'), name='artists-by-name'),
    path('Artists/newest/', artists_views.ArtistsView.as_view(list_type='newest'), name='artists-by-newest'),
    path('Artists/recently_active/', artists_views.ArtistsView.as_view(list_type='recently_active'), name='artists-by-recently-active'),
    path('Artists/top_rated/', artists_views.ArtistsView.as_view(list_type='top_rated'), name='artists-by-top-rated'),
    path('Artists/top_rated_active/', artists_views.ArtistsView.as_view(list_type='top_rated_active'), name='artists-by-top-rated-active'),
    path('Artists/most_prolific/', artists_views.ArtistsView.as_view(list_type='most_prolific'), name='artists-by-most-prolific'),
    path('Artists/random/', artists_views.ArtistsView.as_view(list_type='random'), name='artists-by-random'),
    path('Artists/search/', artists_views.ArtistsView.as_view(list_type='search'), name='artists-by-search'),

    url(r'^Artists/(?P<dir_name>[^/]+)/$', fanart_views.ArtistView.as_view(), name='artist'),
    url(r'^Artists/(?P<dir_name>[^/]+)/Gallery/(?:(?P<subview>[a-z]+)/)?$', fanart_views.ArtistGalleryView.as_view(), name='artist-gallery'),
    url(r'^Artists/(?P<dir_name>[^/]+)/ArtWall/$', fanart_views.ArtWallView.as_view(), name='artist-artwall'),
    # url(r'^Artists/(?P<dir_name>[^/]+)/Characters/$', fanart_views.CharactersView.as_view(), name='artist-characters'),

    path('artists/list/newest/', artists_views.ArtistsListByNewestView.as_view(), name='artists-list-by-newest'),
    path('artists/list/recently_active/', artists_views.ArtistsListByRecentlyActiveView.as_view(), name='artists-list-by-recently-active'),
    path('artists/list/top_rated/', artists_views.ArtistsListByTopRatedView.as_view(), name='artists-list-by-top-rated'),
    path('artists/list/top_rated_active/', artists_views.ArtistsListByTopRatedActiveView.as_view(), name='artists-list-by-top-rated-active'),
    path('artists/list/most_prolific/', artists_views.ArtistsListByMostProlificView.as_view(), name='artists-list-by-most-prolific'),
    path('artists/list/random/', artists_views.ArtistsListByRandomView.as_view(), name='artists-list-by-random'),
    path('artists/list/search/', artists_views.ArtistsListBySearchView.as_view(), name='artists-list-by-search'),

    path('Artwork/', artwork_views.ArtworkView.as_view(), name='artwork'),
    path('Artwork/newest/', artwork_views.ArtworkView.as_view(list_type='newest'), name='artwork-by-newest'),
    path('Artwork/tag/', artwork_views.ArtworkView.as_view(list_type='tag'), name='artwork-by-tag'),
    path('Artwork/unviewed/', artwork_views.ArtworkView.as_view(list_type='unviewed'), name='artwork-by-unviewed'),
    path('Artwork/newest_by_faves/', artwork_views.ArtworkView.as_view(list_type='newest_by_faves'), name='artwork-by-newest-by-faves'),
    path('Artwork/top_rated/', artwork_views.ArtworkView.as_view(list_type='top_rated'), name='artwork-by-top-rated'),
    path('Artwork/top_rated_recent/', artwork_views.ArtworkView.as_view(list_type='top_rated_recent'), name='artwork-by-top-rated-recent'),
    path('Artwork/random/', artwork_views.ArtworkView.as_view(list_type='random'), name='artwork-by-random'),
    path('Artwork/search/', artwork_views.ArtworkView.as_view(list_type='search'), name='artwork-by-search'),
    path('Artwork/character/', artwork_views.ArtworkView.as_view(list_type='character'), name='artwork-by-character'),

    path('artwork/list/newest/', artwork_views.ArtworkListByNewestView.as_view(), name='artwork-list-by-newest'),
    path('artwork/list/unviewed/', artwork_views.ArtworkListByUnviewedView.as_view(), name='artwork-list-by-unviewed'),
    path('artwork/list/newest_by_faves/', artwork_views.ArtworkListByNewestByFavesView.as_view(), name='artwork-list-by-newest-by-faves'),
    path('artwork/list/top_rated/', artwork_views.ArtworkListByTopRatedView.as_view(), name='artwork-list-by-top-rated'),
    path('artwork/list/top_rated_recent/', artwork_views.ArtworkListByTopRatedRecentView.as_view(), name='artwork-list-by-top-rated-recent'),
    path('artwork/list/random/', artwork_views.ArtworkListByRandomView.as_view(), name='artwork-list-by-random'),
    path('artwork/list/search/', artwork_views.ArtworkListSearchByTermView.as_view(), name='artwork-list-search-by-term'),
    path('artwork/list/tag/', artwork_views.ArtworkListSearchByTagView.as_view(), name='artwork-list-search-by-tag'),
    path('artwork/list/character/', artwork_views.ArtworkListSearchByCharacterView.as_view(), name='artwork-list-search-by-character'),

    path('Characters/', characters_views.CharactersView.as_view(), name='characters'),
    path('Characters/canon/', characters_views.CharactersView.as_view(list_type='canon'), name='characters-by-canon'),
    path('Characters/newest/', characters_views.CharactersView.as_view(list_type='newest'), name='characters-by-newest'),
    path('Characters/most_tagged/', characters_views.CharactersView.as_view(list_type='most_tagged'), name='characters-by-most-tagged'),
    path('Characters/recently_tagged/', characters_views.CharactersView.as_view(list_type='recently_tagged'), name='characters-by-recently-tagged'),
    path('Characters/search/', characters_views.CharactersView.as_view(list_type='search'), name='characters-by-search'),
    path('Artists/<str:dir_name>/Characters/', characters_views.CharactersView.as_view(list_type='artist', tab_selected='search'), name='artist-characters'),

    path('characters/species/', characters_views.CharactersSpeciesView.as_view(), name='characters-species-list'),
    path('characters/list/canon/', characters_views.CharactersListByCanonView.as_view(), name='characters-list-by-canon'),
    path('characters/list/newest/', characters_views.CharactersListByNewestView.as_view(), name='characters-list-by-newest'),
    path('characters/list/most_tagged/', characters_views.CharactersListByMostTaggedView.as_view(), name='characters-list-by-most-tagged'),
    path('characters/list/recently_tagged/', characters_views.CharactersListByRecentlyTaggedView.as_view(), name='characters-list-by-recently-tagged'),
    path('characters/list/search/', characters_views.CharactersListSearchView.as_view(), name='characters-list-search'),
    path('characters/list/species/', characters_views.CharactersListSearchBySpeciesView.as_view(), name='characters-list-search-by-species'),
    path('characters/list/artist/', characters_views.CharactersListByArtistView.as_view(), name='characters-list-by-artist'),

    # Chamber of Stars

    path('ChamberOfStars/', RedirectView.as_view(url='/FeaturedArtwork/'), name='chamber-of-stars'),

    # Showcases
    path('Showcases/', stars_views.ShowcasesView.as_view(), name='showcases'),
    path('Showcases/<int:showcase_id>/', stars_views.ShowcaseView.as_view(), name='showcase'),

    # Featured Artists and Featured Pictures
    path('FeaturedArtists/', stars_views.FeaturedArtistsView.as_view(), name='featured-artists'),
    path('FeaturedArtists/<month:month_featured>/', stars_views.FeaturedArtistView.as_view(), name='featured-artist'),
    path('FeaturedArtwork/', stars_views.FeaturedPicturesView.as_view(), name='featured-pictures'),

    # Contests
    path('Contests/', contests.ContestsView.as_view(), name='contests'),
    path('Contests/global/', contests.ContestsGlobalView.as_view(), name='contests-global'),
    path('Contests/personal/', contests.ContestsPersonalView.as_view(), name='contests-personal'),
    path('contest/', include('tlkfaa.urls.contests')),

    url(r'^Artwork/offers/(?P<offer_id>[0-9]+)\.(?P<ext>[a-z]+)$', trading_tree_views.OfferRedirectView.as_view(), name='offer-redirect'),
    url(r'^Picture.jsp$', fanart_views.PictureRedirectByIDView.as_view(), name='picture-redirect'),
    url(r'^Artists/(?P<dir_name>[^/]+)/(?P<filename>[^/]+)$', fanart_views.PictureRedirectByPathView.as_view(), name='picture-redirect'),

    url(r'^picture/(?P<picture_id>[0-9]+)/fans/$', fanart_views.PictureFansView.as_view(), name='picture-fans'),
    url(r'^picture/(?P<picture_id>[0-9]+)/', fanart_views.PictureView.as_view(), name='picture'),
    url(r'^character/(?P<character_id>[0-9]+)/$', characters_views.CharacterView.as_view(), name='character'),

    url(r'^comments/(?P<picture_id>[0-9]+)/$', fanart_views.CommentsView.as_view(), name='comments'),
    url(r'^comments/(?P<picture_id>[0-9]+)/reply/$', fanart_views.PostCommentView.as_view(), name='post-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/detail/$', fanart_views.CommentDetailView.as_view(), name='comment-detail'),
    url(r'^comment/(?P<comment_id>[0-9]+)/edit/$', fanart_views.EditCommentView.as_view(), name='edit-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/delete/$', fanart_views.DeleteCommentView.as_view(), name='delete-comment'),

    url(r'^shouts/(?P<artist_id>[0-9]+)/$', fanart_views.ShoutsView.as_view(), name='shouts'),
    url(r'^shouts/(?P<artist_id>[0-9]+)/post/$', fanart_views.PostShoutView.as_view(), name='post-shout'),
    url(r'^shouts/(?P<pk>[0-9]+)/detail/$', fanart_views.ShoutDetailView.as_view(), name='shout-detail'),
    url(r'^shouts/(?P<pk>[0-9]+)/edit/$', fanart_views.EditShoutView.as_view(), name='edit-shout'),
    url(r'^shouts/(?P<shout_id>[0-9]+)/reply/$', fanart_views.ReplyShoutView.as_view(), name='reply-shout'),
    url(r'^shouts/(?P<shout_id>[0-9]+)/delete/$', fanart_views.DeleteShoutView.as_view(), name='delete-shout'),

#    url(r'^comments/mark_read/$', fanart_views.MarkCommentsReadView.as_view(), name='mark-comments-read'),
#    url(r'^shouts/mark_read/$', fanart_views.MarkShoutsReadView.as_view(), name='mark-shouts-read'),

    url(r'^folders/(?P<artist_id>[0-9]+)/$', fanart_views.FoldersView.as_view(), name='folders'),
    # url(r'^artwork/(?P<list>[a-z]+)/$', fanart_views.ArtworkListView.as_view(), name='artwork-list'),
    # url(r'^characters/species/$', fanart_views.CharactersSpeciesView.as_view(), name='characters-species'),
    # url(r'^characters/(?P<list>[a-z]+)/$', fanart_views.CharactersListView.as_view(), name='characters-list'),

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
    path('flag_spam/<int:comment_id>/', fanart_views.FlagSpamView.as_view(), name='flag-spam'),

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
    url(r'^bulletin/(?P<bulletin_id>[0-9]+)/reply/$', fanart_views.PostBulletinReplyView.as_view(), name='post-bulletin-reply'),

    url(r'^aotm/vote/$', fanart_views.AotmVoteView.as_view(), name='aotm-vote'),
    url(r'^aotm/vote/form/$', fanart_views.AotmVoteFormView.as_view(), name='aotm-vote-form'),

    url(r'^social_media/identities/$', fanart_views.SocialMediaIdentitiesView.as_view(), name='social-media-identities'),
    url(r'^social_media/add/$', fanart_views.AddSocialMediaIdentityView.as_view(), name='add-social-media-identity'),
    url(r'^social_media/(?P<identity_id>[0-9]+)/remove/$', fanart_views.RemoveSocialMediaIdentityView.as_view(), name='remove-social-media-identity'),

    url(r'^profile-pic/upload/$', fanart_views.UploadProfilePicView.as_view(), name='upload-profile-pic'),
    url(r'^profile-pic/upload/status/$', fanart_views.ProfilePicStatusView.as_view(), name='profile-pic-status'),
    url(r'^profile-pic/remove/$', fanart_views.RemoveProfilePicView.as_view(), name='remove-profile-pic'),

    url(r'^banner/upload/$', fanart_views.UploadBannerView.as_view(), name='upload-banner'),
    url(r'^banner/remove/$', fanart_views.RemoveBannerView.as_view(), name='remove-banner'),

    url(r'^browser-stats/$', fanart_views.BrowserStatsView.as_view(), name='browser-stats'),

    url(r'^ArtManager/', include(('artmanager.urls', 'artmanager'), namespace='artmanager')),

    path('wiki/notifications/', include('django_nyt.urls')),
    path('wiki/', include('wiki.urls')),

    # path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler500 = lambda request: fanart_views.ErrorHandler500.as_view()(request)
# handler404 = lambda request: fanart_views.ErrorHandler404.as_view()(request)
# handler403 = lambda request: fanart_views.ErrorHandler403.as_view()(request)
