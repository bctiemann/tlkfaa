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
    url(r'^prefs/update/$', artmanager_views.PrefsUpdateView.as_view(), name='prefs-update'),
    url(r'^prefs/update/profile/$', artmanager_views.PrefsUpdateProfileView.as_view(), name='prefs-update-profile'),
    url(r'^prefs/usermode/$', artmanager_views.UserModeView.as_view(), name='prefs-usermode'),

    url(r'^upload/(?:(?P<pending_id>[0-9]+)/)?$', artmanager_views.UploadView.as_view(), name='upload'),
    url(r'^upload/form/$', artmanager_views.UploadFormView.as_view(), name='upload-form'),
    url(r'^upload/submit/$', artmanager_views.UploadFileView.as_view(), name='upload-file'),
    url(r'^upload/success/(?P<pending_id>[0-9]+)/$', artmanager_views.UploadSuccessView.as_view(), name='upload-success'),

    url(r'^pending/$', artmanager_views.PendingView.as_view(), name='pending'),
    url(r'^pending/(?P<pending_id>[0-9]+)/$', artmanager_views.PendingDetailView.as_view(), name='pending-detail'),
    url(r'^pending/(?P<pending_id>[0-9]+)/edit/$', artmanager_views.PendingFormView.as_view(), name='pending-form'),
    url(r'^pending/(?P<pending_id>[0-9]+)/update/$', artmanager_views.PendingUpdateView.as_view(), name='update-pending'),
    url(r'^pending/(?P<pending_id>[0-9]+)/delete/$', artmanager_views.PendingDeleteView.as_view(), name='delete-pending'),
    url(r'^pending/status/$', artmanager_views.PendingStatusView.as_view(), name='pending-status'),

    url(r'^artwork/$', artmanager_views.ArtworkView.as_view(), name='artwork'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/$', artmanager_views.PictureDetailView.as_view(), name='artwork-picture-detail'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/edit/$', artmanager_views.PictureFormView.as_view(), name='artwork-picture-form'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/update/$', artmanager_views.PictureUpdateView.as_view(), name='artwork-update-picture'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/$', artmanager_views.ColoringPictureDetailView.as_view(), name='artwork-coloring-picture-detail'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/edit/$', artmanager_views.ColoringPictureFormView.as_view(), name='artwork-coloring-picture-form'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/update/$', artmanager_views.ColoringPictureUpdateView.as_view(), name='artwork-update-coloring-picture'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/delete/$', artmanager_views.ColoringPictureDeleteView.as_view(), name='artwork-delete-coloring-picture'),
    url(r'^artwork/tag_characters/(?P<obj>(new|[0-9]+))/$', artmanager_views.TagCharactersView.as_view(), name='tag-characters'),

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
