from django.urls import path

from fanart.views import approval


urlpatterns = [
    path('', approval.ApprovalHomeView.as_view(), name='approve'),
    path('list/', approval.PendingListView.as_view(), name='pending-list'),
    path('count/', approval.PendingCountView.as_view(), name='pending-count'),
    path('<int:pending_id>/', approval.PendingDetailView.as_view(), name='pending-detail'),
    path('<int:pending_id>/approve/', approval.PendingApproveView.as_view(), name='pending-approve'),
    path('<int:pending_id>/reject/', approval.PendingRejectView.as_view(), name='pending-reject'),
    path('<int:pending_id>/resize/', approval.PendingResizeView.as_view(), name='pending-resize'),
    path('<int:pending_id>/convert/', approval.PendingConvertView.as_view(), name='pending-convert'),
    path('<int:pending_id>/upload_thumb/', approval.PendingUploadThumbView.as_view(), name='pending-upload-thumb'),
    path('thumb_status/', approval.PendingThumbStatusView.as_view(), name='pending-thumb-status'),
    path('auto_approval/<int:artist_id>/', approval.AutoApprovalView.as_view(), name='pending-auto-approval'),
    path('mod_notes/<int:artist_id>/', approval.ModNotesView.as_view(), name='pending-mod-notes'),
    path('mod_notes/<int:artist_id>/add/', approval.AddModNoteView.as_view(), name='pending-mod-notes-add'),
]
