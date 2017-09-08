from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from fanart import views as fanart_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', fanart_views.HomeView.as_view(), name='home'),
    url(r'^Artwork/$', fanart_views.ArtworkView.as_view(), name='artwork'),
    url(r'^Artists/$', fanart_views.ArtistsView.as_view(), name='artists'),
    url(r'^Characters/$', fanart_views.CharactersView.as_view(), name='characters'),
    url(r'^TradingTree/$', fanart_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^ColoringCave/$', fanart_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^Special/$', fanart_views.SpecialFeaturesView.as_view(), name='special'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
