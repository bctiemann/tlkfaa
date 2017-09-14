from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import RedirectView

from artmanager import views as artmanager_views

urlpatterns = [
    url(r'^$', artmanager_views.BaseRedirectView.as_view(), name='home'),
#        RedirectView.as_view(
#            url='dashboard',
#            permanent=False),
#        name='home'
#    ),
    url(r'^dashboard/$', artmanager_views.DashboardView.as_view(), name='dashboard'),
    url(r'^prefs/$', artmanager_views.PrefsView.as_view(), name='prefs'),
    url(r'^upload/$', artmanager_views.UploadView.as_view(), name='upload'),
    url(r'^artwork/$', artmanager_views.ArtworkView.as_view(), name='artwork'),
    url(r'^folders/$', artmanager_views.FoldersView.as_view(), name='folders'),
    url(r'^artwall/$', artmanager_views.ArtWallView.as_view(), name='artwall'),
    url(r'^characters/$', artmanager_views.CharactersView.as_view(), name='characters'),
    url(r'^customize/$', artmanager_views.CustomizeView.as_view(), name='customize'),
    url(r'^private_msgs/$', artmanager_views.PrivateMessagesView.as_view(), name='private-msgs'),
    url(r'^trading_tree/$', artmanager_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^coloring_cave/$', artmanager_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^contests/$', artmanager_views.ContestsView.as_view(), name='contests'),
    url(r'^bulletins/$', artmanager_views.BulletinsView.as_view(), name='bulletins'),
    url(r'^upload_history/$', artmanager_views.UploadHistoryView.as_view(), name='upload-history'),
    url(r'^comments/$', artmanager_views.CommentsView.as_view(), name='comments'),
    url(r'^shouts/$', artmanager_views.ShoutsView.as_view(), name='shouts'),
    url(r'^fans/$', artmanager_views.FansView.as_view(), name='fans'),
    url(r'^blocks/$', artmanager_views.BlocksView.as_view(), name='blocks'),
]