from django.urls import include, re_path, path
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import RedirectView

from artmanager import views as artmanager_views
from artmanager.views import contests as contests_views
from artmanager.views import bulletins as bulletins_views
from artmanager.views import shouts as shouts_views
from artmanager.views import comments as comments_views

urlpatterns = [
    path('', artmanager_views.BaseRedirectView.as_view(), name='home'),
#        RedirectView.as_view(
#            url='dashboard',
#            permanent=False),
#        name='home'
#    ),
    path('dashboard/', artmanager_views.DashboardView.as_view(), name='dashboard'),

    path('prefs/', artmanager_views.PrefsView.as_view(), name='prefs'),
    path('prefs/update/', artmanager_views.PrefsUpdateView.as_view(), name='prefs-update'),
    path('prefs/update/profile/', artmanager_views.PrefsUpdateProfileView.as_view(), name='prefs-update-profile'),
    path('prefs/usermode/', artmanager_views.UserModeView.as_view(), name='prefs-usermode'),

    path('upload/', artmanager_views.UploadView.as_view(), name='upload'),
    path('upload/<int:pending_id>/', artmanager_views.UploadView.as_view(), name='upload'),
    path('upload/form/', artmanager_views.UploadFormView.as_view(), name='upload-form'),
    path('upload/submit/', artmanager_views.UploadFileView.as_view(), name='upload-file'),
    path('upload/success/<int:pending_id>/', artmanager_views.UploadSuccessView.as_view(), name='upload-success'),

    path('pending/', artmanager_views.PendingView.as_view(), name='pending'),
    path('pending/<int:pending_id>/', artmanager_views.PendingDetailView.as_view(), name='pending-detail'),
    path('pending/<int:pending_id>/edit/', artmanager_views.PendingFormView.as_view(), name='pending-form'),
    path('pending/<int:pending_id>/update/', artmanager_views.PendingUpdateView.as_view(), name='pending-update'),
    path('pending/<int:pending_id>/delete/', artmanager_views.PendingDeleteView.as_view(), name='pending-delete'),
    path('pending/status/', artmanager_views.PendingStatusView.as_view(), name='pending-status'),

    path('artwork/', artmanager_views.ArtworkView.as_view(), name='artwork'),
    path('artwork/picture/<int:picture_id>/', artmanager_views.PictureDetailView.as_view(), name='artwork-picture-detail'),
    path('artwork/picture/<int:picture_id>/edit/', artmanager_views.PictureFormView.as_view(), name='artwork-picture-form'),
    path('artwork/picture/<int:picture_id>/update/', artmanager_views.PictureUpdateView.as_view(), name='artwork-update-picture'),
    path('artwork/picture/<int:picture_id>/delete/', artmanager_views.PictureDeleteView.as_view(), name='artwork-delete-picture'),
    path('artwork/picture/<picture_ids>/delete/', artmanager_views.PictureBulkDeleteView.as_view(), name='artwork-bulk-delete-picture'),
    path('artwork/picture/<picture_ids>/move/', artmanager_views.PictureBulkMoveView.as_view(), name='artwork-bulk-move-picture'),
    path('artwork/picture/<int:picture_id>/gift/', artmanager_views.GiftPictureListView.as_view(), name='artwork-gift-picture-list'),
    path('artwork/picture/<int:picture_id>/gift/form/', artmanager_views.GiftPictureFormView.as_view(), name='artwork-gift-picture-form'),
    path('artwork/picture/<int:picture_id>/gift/send/', artmanager_views.GiftPictureSendView.as_view(), name='artwork-gift-picture-send'),
    path('artwork/picture/<int:gift_picture_id>/gift/delete/', artmanager_views.GiftPictureDeleteView.as_view(), name='artwork-gift-picture-delete'),
    path('artwork/picture/<int:picture_id>/set_example/', artmanager_views.SetExamplePictureView.as_view(), name='artwork-set-example-picture'),
    path('artwork/coloring_picture/<int:coloring_picture_id>/', artmanager_views.ColoringPictureDetailView.as_view(), name='artwork-coloring-picture-detail'),
    path('artwork/coloring_picture/<int:coloring_picture_id>/edit/', artmanager_views.ColoringPictureFormView.as_view(), name='artwork-coloring-picture-form'),
    path('artwork/coloring_picture/<int:coloring_picture_id>/update/', artmanager_views.ColoringPictureUpdateView.as_view(), name='artwork-update-coloring-picture'),
    path('artwork/coloring_picture/<int:coloring_picture_id>/delete/', artmanager_views.ColoringPictureDeleteView.as_view(), name='artwork-delete-coloring-picture'),
    path('artwork/coloring_picture/<coloring_picture_ids>/delete/', artmanager_views.ColoringPictureBulkDeleteView.as_view(), name='artwork-bulk-delete-coloring-picture'),
    path('artwork/coloring/status/', artmanager_views.ColoringStatusView.as_view(), name='artwork-coloring-status'),
    path('artwork/tag_characters/<obj>/', artmanager_views.TagCharactersView.as_view(), name='tag-characters'),
    path('artwork/zip_gallery/', artmanager_views.ArtworkDownloadZIPView.as_view(), name='zip-gallery'),

    path('folders/', artmanager_views.FoldersView.as_view(), name='folders'),
    path('folders/create/', artmanager_views.FolderCreateView.as_view(), name='folder-create'),
    path('folders/<int:folder_id>/update/', artmanager_views.FolderUpdateView.as_view(), name='folder-update'),
    path('folders/<int:folder_id>/delete/', artmanager_views.FolderDeleteView.as_view(), name='folder-delete'),

    path('art_trades_requests/', artmanager_views.ArtTradesRequestsView.as_view(), name='art-trades-requests'),
    path('art_trades_requests/<int:gift_picture_id>/accept/', artmanager_views.GiftPictureAcceptView.as_view(), name='art-trades-requests-gift-picture-accept'),
    path('art_trades_requests/<gift_picture_ids>/delete/', artmanager_views.GiftPictureBulkDeleteView.as_view(), name='art-trades-requests-gift-picture-bulk-delete'),

    path('characters/', artmanager_views.CharactersView.as_view(), name='characters'),
    path('characters/create/', artmanager_views.CharacterCreateView.as_view(), name='character-create'),
    path('characters/<int:character_id>/', artmanager_views.CharacterDetailView.as_view(), name='character-detail'),
    path('characters/<int:character_id>/form/', artmanager_views.CharacterFormView.as_view(), name='character-form'),
    path('characters/<int:character_id>/update/', artmanager_views.CharacterUpdateView.as_view(), name='character-update'),
    path('characters/<int:character_id>/delete/', artmanager_views.CharacterDeleteView.as_view(), name='character-delete'),
    path('characters/<int:character_id>/set_picture/', artmanager_views.CharacterSetPictureView.as_view(), name='character-set-picture'),

    path('customize/', artmanager_views.CustomizeView.as_view(), name='customize'),
    path('customize/banner_preview/', artmanager_views.BannerPreviewView.as_view(), name='customize-banner-preview'),

    path('private_msgs/', artmanager_views.PrivateMessagesView.as_view(), name='private-msgs'),
    path('private_msgs/in/', artmanager_views.PrivateMessagesView.as_view(box='in'), name='private-msgs-in'),
    path('private_msgs/out/', artmanager_views.PrivateMessagesView.as_view(box='out'), name='private-msgs-out'),
    path('private_msgs/trash/', artmanager_views.PrivateMessagesView.as_view(box='trash'), name='private-msgs-trash'),
    path('private_msgs/<int:pm_id>/', artmanager_views.PrivateMessagesView.as_view(), name='private-msgs'),
    path('private_msgs/user/', artmanager_views.PrivateMessagesView.as_view(), name='private-msgs-user'),
    path('private_msgs/user/<int:recipient_id>/', artmanager_views.PrivateMessagesView.as_view(), name='private-msgs-user'),

    path('trading_tree/', artmanager_views.TradingTreeView.as_view(), name='trading-tree'),
    path('trading_tree/<str:offer_type>/', artmanager_views.TradingTreeView.as_view(), name='trading-tree'),
    path('trading_tree/for_you/', artmanager_views.TradingTreeForYouView.as_view(), name='trading-tree-for-you'),
    path('trading_tree/for_you/<str:offer_type>/', artmanager_views.TradingTreeForYouView.as_view(), name='trading-tree-for-you'),
    path('trading_tree/icon/upload/', artmanager_views.UploadIconOfferView.as_view(), name='upload-icon-offer'),
    path('trading_tree/adoptable/create/', artmanager_views.CreateAdoptableOfferView.as_view(), name='create-adoptable-offer'),
    path('trading_tree/<int:offer_id>/status/', artmanager_views.OfferStatusView.as_view(), name='offer-status'),

    path('coloring_cave/', artmanager_views.ColoringCaveView.as_view(), name='coloring-cave'),
    path('coloring_cave/<int:coloring_base_id>/', artmanager_views.ColoringCaveView.as_view(), name='coloring-cave'),
    path('coloring_cave/<int:picture_id>/post/', artmanager_views.ColoringBasePostView.as_view(), name='coloring-base-post'),
    path('coloring_cave/<int:coloring_base_id>/remove/', artmanager_views.ColoringBaseRemoveView.as_view(), name='coloring-base-remove'),
    path('coloring_cave/<int:coloring_base_id>/restore/', artmanager_views.ColoringBaseRestoreView.as_view(), name='coloring-base-restore'),

    path('contests/', contests_views.ContestsView.as_view(), name='contests'),
    path('contests/create/', contests_views.ContestCreateView.as_view(), name='contest-create'),
    path('contests/<int:contest_id>/update/', contests_views.ContestUpdateView.as_view(), name='contest-update'),
    path('contests/<int:contest_id>/publish/', contests_views.ContestPublishView.as_view(), name='contest-publish'),
    path('contests/<int:contest_id>/unpublish/', contests_views.ContestPublishView.as_view(), name='contest-unpublish'),
    path('contests/<int:contest_id>/delete/', contests_views.ContestDeleteView.as_view(), name='contest-delete'),
    path('contests/<int:contest_id>/cancel/', contests_views.ContestCancelView.as_view(), name='contest-cancel'),
    path('contests/<int:contest_id>/entries/', contests_views.ContestEntriesView.as_view(), name='contest-entries'),
#    re_path(r'^contests/(?P<contest_id>[0-9]+)/remove_picture/(?P<picture_id>[0-9]+)/$', contests_views.ContestRemovePictureView.as_view(), name='contest-remove-picture'),

    path('bulletins/', bulletins_views.BulletinsView.as_view(), name='bulletins'),
    path('bulletins/create/', bulletins_views.BulletinCreateView.as_view(), name='bulletin-create'),
    path('bulletins/<int:bulletin_id>/update/', bulletins_views.BulletinUpdateView.as_view(), name='bulletin-update'),
    path('bulletins/<int:bulletin_id>/delete/', bulletins_views.BulletinDeleteView.as_view(), name='bulletin-delete'),

    path('upload_history/', artmanager_views.UploadHistoryView.as_view(), name='upload-history'),

    path('comments/', comments_views.CommentsView.as_view(), name='comments'),
    path('comments/mark_read/', comments_views.MarkCommentsReadView.as_view(), name='mark-comments-read'),
    path('comments/<str:comment_type>/', comments_views.CommentsView.as_view(), name='comments'),
    path('comments/<int:comment_id>/', comments_views.CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/delete/', comments_views.CommentDeleteView.as_view(), name='comment-delete'),

    path('shouts/', shouts_views.ShoutsView.as_view(), name='shouts'),
    path('shouts/mark_read/', shouts_views.MarkShoutsReadView.as_view(), name='mark-shouts-read'),
    path('shouts/<int:shout_id>/', shouts_views.ShoutDetailView.as_view(), name='shout-detail'),
    path('shouts/<int:shout_id>/delete/', shouts_views.ShoutDeleteView.as_view(), name='shout-delete'),
    path('shouts/<str:shout_type>/', shouts_views.ShoutsView.as_view(), name='shouts'),

    path('fans/', artmanager_views.FansView.as_view(), name='fans'),
    path('blocks/', artmanager_views.BlocksView.as_view(), name='blocks'),
]
