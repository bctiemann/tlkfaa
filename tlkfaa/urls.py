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
    url(r'^Artwork/$', fanart_views.ArtworkView.as_view(), name='artwork'),
    url(r'^Artists/$', fanart_views.ArtistsView.as_view(), name='artists'),
    url(r'^Characters/$', fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^TradingTree/$', fanart_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^ColoringCave/$', fanart_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^Special/$', fanart_views.SpecialFeaturesView.as_view(), name='special'),

    url(r'^userbox/set/(?P<box>[a-z_]+)/(?P<show>[01]+)$', fanart_views.UserBoxSetView.as_view(), name='userbox-set'),
    url(r'^userbox/favorite_artists_box/$', fanart_views.FavoriteArtistsBoxView.as_view(), name='favorite-artists-box'),
    url(r'^userbox/favorite_pictures_box/$', fanart_views.FavoritePicturesBoxView.as_view(), name='favorite-pictures-box'),
    url(r'^userbox/sketcher_box/$', fanart_views.SketcherBoxView.as_view(), name='sketcher-box'),
    url(r'^userbox/community_art_box/$', fanart_views.CommunityArtBoxView.as_view(), name='community-art-box'),
    url(r'^userbox/contests_box/$', fanart_views.ContestsBoxView.as_view(), name='contests-box'),
    url(r'^userbox/tool_box/$', fanart_views.ToolBoxView.as_view(), name='tool-box'),

    url(r'^Artwork/Artists/(?P<dir_name>[^/]+)/(?:(?P<subview>[a-z]+)/)?$', fanart_views.ArtistView.as_view(), name='artist'),

    url(r'^picture/(?P<picture_id>[0-9]+)/$', fanart_views.PictureView.as_view(), name='picture'),

    url(r'^comments/(?P<picture_id>[0-9]+)/$', fanart_views.CommentsView.as_view(), name='comments'),
    url(r'^comments/(?P<picture_id>[0-9]+)/reply/$', fanart_views.PostCommentView.as_view(), name='post-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/detail/$', fanart_views.CommentDetailView.as_view(), name='comment-detail'),
    url(r'^comment/(?P<comment_id>[0-9]+)/edit/$', fanart_views.EditCommentView.as_view(), name='edit-comment'),
    url(r'^comment/(?P<comment_id>[0-9]+)/delete/$', fanart_views.DeleteCommentView.as_view(), name='delete-comment'),

    url(r'^shouts/(?P<artist_id>[0-9]+)/$', fanart_views.ShoutsView.as_view(), name='shouts'),
    url(r'^shouts/(?P<artist_id>[0-9]+)/post/$', fanart_views.PostShoutView.as_view(), name='post-shouts'),
    url(r'^shout/(?P<shout_id>[0-9]+)/delete/$', fanart_views.DeleteShoutView.as_view(), name='delete-shout'),

    url(r'^fave/(?P<fave_type>[a-z]+)/(?P<object_id>[0-9]+)/$', fanart_views.ToggleFaveView.as_view(), name='toggle-fave'),
    url(r'^block/(?P<user_id>[0-9]+)/$', fanart_views.ToggleBlockView.as_view(), name='toggle-block'),

    url(r'^tooltip/picture/(?P<picture_id>[0-9]+)/$', fanart_views.PictureTooltipView.as_view(), name='picture-tooltip'),
    url(r'^tooltip/coloring_picture/(?P<coloring_picture_id>[0-9]+)/$', fanart_views.ColoringPictureTooltipView.as_view(), name='coloring-picture-tooltip'),

    url(r'^admin_announcements/(?P<count>[0-9]+)/(?P<start>[0-9]+)/$', fanart_views.AdminAnnouncementsView.as_view(), name='admin-announcements'),
    url(r'^bulletins/(?P<count>[0-9]+)/(?P<start>[0-9]+)/$', fanart_views.BulletinsView.as_view(), name='admin-announcements'),

    url(r'^ArtManager/', include('artmanager.urls', 'artmanager')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
