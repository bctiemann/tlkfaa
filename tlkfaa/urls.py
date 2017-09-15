from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from django.contrib.auth import views as auth_views
from fanart import views as fanart_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(
        r'^login/$',
        auth_views.LoginView.as_view(),
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

    url(r'^userbox/set/(?P<box>[a-z_]+)/(?P<show>[01]+)', fanart_views.UserBoxSetView.as_view(), name='userbox-set'),
    url(r'^userbox/favorite_artists', fanart_views.FavoriteArtistsBoxView.as_view(), name='favorite-artists-box'),
    url(r'^userbox/favorite_pictures', fanart_views.FavoritePicturesBoxView.as_view(), name='favorite-pictures-box'),

    url(r'^ArtManager/', include('artmanager.urls', 'artmanager')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
