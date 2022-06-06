from django.urls import path

from fanart.views import contests


urlpatterns = [
    path('<int:contest_id>/', contests.ContestView.as_view(), name='contest'),
    path('<int:contest_id>/entry/create/', contests.ContestEntryCreateView.as_view(), name='contest-entry-create'),
    path('entry/<int:entry_id>/delete/', contests.ContestEntryDeleteView.as_view(), name='contest-entry-delete'),
    path('<int:contest_id>/vote/', contests.ContestVoteView.as_view(), name='contest-vote'),
    path('setup/', contests.ContestSetupView.as_view(), name='contest-setup'),
    path('setup/success/', contests.ContestSetupSuccessView.as_view(), name='contest-setup-success'),
]
