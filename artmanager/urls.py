from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import RedirectView

from artmanager import views as artmanager_views
from artmanager.views import contests as contests_views
from artmanager.views import bulletins as bulletins_views

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
    url(r'^pending/(?P<pending_id>[0-9]+)/update/$', artmanager_views.PendingUpdateView.as_view(), name='pending-update'),
    url(r'^pending/(?P<pending_id>[0-9]+)/delete/$', artmanager_views.PendingDeleteView.as_view(), name='pending-delete'),
    url(r'^pending/status/$', artmanager_views.PendingStatusView.as_view(), name='pending-status'),

    url(r'^artwork/$', artmanager_views.ArtworkView.as_view(), name='artwork'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/$', artmanager_views.PictureDetailView.as_view(), name='artwork-picture-detail'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/edit/$', artmanager_views.PictureFormView.as_view(), name='artwork-picture-form'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/update/$', artmanager_views.PictureUpdateView.as_view(), name='artwork-update-picture'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/delete/$', artmanager_views.PictureDeleteView.as_view(), name='artwork-delete-picture'),
    url(r'^artwork/picture/(?P<picture_ids>[0-9,]+)/delete/$', artmanager_views.PictureBulkDeleteView.as_view(), name='artwork-bulk-delete-picture'),
    url(r'^artwork/picture/(?P<picture_ids>[0-9,]+)/move/$', artmanager_views.PictureBulkMoveView.as_view(), name='artwork-bulk-move-picture'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/gift/$', artmanager_views.GiftPictureListView.as_view(), name='artwork-gift-picture-list'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/gift/form/$', artmanager_views.GiftPictureFormView.as_view(), name='artwork-gift-picture-form'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/gift/send/$', artmanager_views.GiftPictureSendView.as_view(), name='artwork-gift-picture-send'),
    url(r'^artwork/picture/(?P<gift_picture_id>[0-9]+)/gift/delete/$', artmanager_views.GiftPictureDeleteView.as_view(), name='artwork-gift-picture-delete'),
    url(r'^artwork/picture/(?P<picture_id>[0-9]+)/set_example/$', artmanager_views.SetExamplePictureView.as_view(), name='artwork-set-example-picture'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/$', artmanager_views.ColoringPictureDetailView.as_view(), name='artwork-coloring-picture-detail'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/edit/$', artmanager_views.ColoringPictureFormView.as_view(), name='artwork-coloring-picture-form'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/update/$', artmanager_views.ColoringPictureUpdateView.as_view(), name='artwork-update-coloring-picture'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_id>[0-9]+)/delete/$', artmanager_views.ColoringPictureDeleteView.as_view(), name='artwork-delete-coloring-picture'),
    url(r'^artwork/coloring_picture/(?P<coloring_picture_ids>[0-9,]+)/delete/$', artmanager_views.ColoringPictureBulkDeleteView.as_view(), name='artwork-bulk-delete-coloring-picture'),
    url(r'^artwork/coloring/status/$', artmanager_views.ColoringStatusView.as_view(), name='artwork-coloring-status'),
    url(r'^artwork/tag_characters/(?P<obj>(new|[0-9]+))/$', artmanager_views.TagCharactersView.as_view(), name='tag-characters'),

    url(r'^folders/$', artmanager_views.FoldersView.as_view(), name='folders'),
    url(r'^folders/create/$', artmanager_views.FolderCreateView.as_view(), name='folder-create'),
    url(r'^folders/(?P<folder_id>[0-9]+)/update/$', artmanager_views.FolderUpdateView.as_view(), name='folder-update'),
    url(r'^folders/(?P<folder_id>[0-9]+)/delete/$', artmanager_views.FolderDeleteView.as_view(), name='folder-delete'),

    url(r'^artwall/$', artmanager_views.ArtWallView.as_view(), name='artwall'),
    url(r'^artwall/(?P<gift_picture_id>[0-9]+)/accept/$', artmanager_views.GiftPictureAcceptView.as_view(), name='artwall-gift-picture-accept'),
    url(r'^artwall/(?P<gift_picture_ids>[0-9,]+)/delete/$', artmanager_views.GiftPictureBulkDeleteView.as_view(), name='artwall-gift-picture-bulk-delete'),

    url(r'^characters/$', artmanager_views.CharactersView.as_view(), name='characters'),
    url(r'^characters/create/$', artmanager_views.CharacterCreateView.as_view(), name='character-create'),
    url(r'^characters/(?P<character_id>[0-9]+)/$', artmanager_views.CharacterDetailView.as_view(), name='character-detail'),
    url(r'^characters/(?P<character_id>[0-9]+)/form/$', artmanager_views.CharacterFormView.as_view(), name='character-form'),
    url(r'^characters/(?P<character_id>[0-9]+)/update/$', artmanager_views.CharacterUpdateView.as_view(), name='character-update'),
    url(r'^characters/(?P<character_id>[0-9]+)/delete/$', artmanager_views.CharacterDeleteView.as_view(), name='character-delete'),
    url(r'^characters/(?P<character_id>[0-9]+)/set_picture/$', artmanager_views.CharacterSetPictureView.as_view(), name='character-set-picture'),

    url(r'^customize/$', artmanager_views.CustomizeView.as_view(), name='customize'),
    url(r'^customize/banner_preview/$', artmanager_views.BannerPreviewView.as_view(), name='customize-banner-preview'),

    url(r'^private_msgs/$', artmanager_views.PrivateMessagesView.as_view(), name='private-msgs'),

    url(r'^trading_tree/(?:(?P<offer_type>(icon|adoptable))/)?$', artmanager_views.TradingTreeView.as_view(), name='trading-tree'),
    url(r'^trading_tree/for_you/(?:(?P<offer_type>(icon|adoptable))/)?', artmanager_views.TradingTreeForYouView.as_view(), name='trading-tree-for-you'),
    url(r'^trading_tree/icon/upload/$', artmanager_views.UploadIconOfferView.as_view(), name='upload-icon-offer'),
    url(r'^trading_tree/adoptable/create/$', artmanager_views.CreateAdoptableOfferView.as_view(), name='create-adoptable-offer'),
    url(r'^trading_tree/(?P<offer_id>[0-9]+)/status/$', artmanager_views.OfferStatusView.as_view(), name='offer-status'),

    url(r'^coloring_cave/(?:(?P<coloring_base_id>[0-9]+)/)?$', artmanager_views.ColoringCaveView.as_view(), name='coloring-cave'),
    url(r'^coloring_cave/(?P<picture_id>[0-9]+)/post/$', artmanager_views.ColoringBasePostView.as_view(), name='coloring-base-post'),
    url(r'^coloring_cave/(?P<coloring_base_id>[0-9]+)/remove/$', artmanager_views.ColoringBaseRemoveView.as_view(), name='coloring-base-remove'),
    url(r'^coloring_cave/(?P<coloring_base_id>[0-9]+)/restore/$', artmanager_views.ColoringBaseRestoreView.as_view(), name='coloring-base-restore'),

    url(r'^contests/$', contests_views.ContestsView.as_view(), name='contests'),
    url(r'^contests/create/$', contests_views.ContestCreateView.as_view(), name='contest-create'),
    url(r'^contests/(?P<contest_id>[0-9]+)/update/$', contests_views.ContestUpdateView.as_view(), name='contest-update'),
    url(r'^contests/(?P<contest_id>[0-9]+)/publish/$', contests_views.ContestPublishView.as_view(), name='contest-publish'),
    url(r'^contests/(?P<contest_id>[0-9]+)/unpublish/$', contests_views.ContestPublishView.as_view(), name='contest-unpublish'),
    url(r'^contests/(?P<contest_id>[0-9]+)/delete/$', contests_views.ContestDeleteView.as_view(), name='contest-delete'),
    url(r'^contests/(?P<contest_id>[0-9]+)/cancel/$', contests_views.ContestCancelView.as_view(), name='contest-cancel'),
#    url(r'^contests/(?P<contest_id>[0-9]+)/remove_picture/(?P<picture_id>[0-9]+)/$', contests_views.ContestRemovePictureView.as_view(), name='contest-remove-picture'),

    url(r'^bulletins/$', bulletins_views.BulletinsView.as_view(), name='bulletins'),
    url(r'^bulletins/create/$', bulletins_views.BulletinCreateView.as_view(), name='bulletin-create'),
    url(r'^bulletins/(?P<bulletin_id>[0-9]+)/update/$', bulletins_views.BulletinUpdateView.as_view(), name='bulletin-update'),
    url(r'^bulletins/(?P<bulletin_id>[0-9]+)/delete/$', bulletins_views.BulletinDeleteView.as_view(), name='bulletin-delete'),

    url(r'^upload_history/$', artmanager_views.UploadHistoryView.as_view(), name='upload-history'),

    url(r'^comments/(?:(?P<comment_type>(received|sent))/)?$', artmanager_views.CommentsView.as_view(), name='comments'),
    url(r'^comments/mark_read/$', artmanager_views.MarkCommentsReadView.as_view(), name='mark-comments-read'),
    url(r'^comments/(?P<comment_id>[0-9]+)/$', artmanager_views.CommentDetailView.as_view(), name='comment-detail'),
    url(r'^comments/(?P<comment_id>[0-9]+)/delete/$', artmanager_views.CommentDeleteView.as_view(), name='comment-delete'),

    url(r'^shouts/(?:(?P<shout_type>(received|sent))/)?$', artmanager_views.ShoutsView.as_view(), name='shouts'),
    url(r'^shouts/mark_read/$', artmanager_views.MarkShoutsReadView.as_view(), name='mark-shouts-read'),
    url(r'^shouts/(?P<shout_id>[0-9]+)/$', artmanager_views.ShoutDetailView.as_view(), name='shout-detail'),
    url(r'^shouts/(?P<shout_id>[0-9]+)/delete/$', artmanager_views.ShoutDeleteView.as_view(), name='shout-delete'),

    url(r'^fans/$', artmanager_views.FansView.as_view(), name='fans'),
    url(r'^blocks/$', artmanager_views.BlocksView.as_view(), name='blocks'),
]
