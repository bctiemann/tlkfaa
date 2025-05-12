from django.urls import path

from fanart.views import prompts


urlpatterns = [
    path('create/', prompts.PromptCreateView.as_view(), name='prompt-create'),
    path('<int:pk>/', prompts.PromptView.as_view(), name='prompt'),
    path('<int:pk>/deactivate/', prompts.PromptDeactivateView.as_view(), name='prompt-deactivate'),
    path('<int:pk>/entry/create/', prompts.PromptEntryCreateView.as_view(), name='prompt-entry-create'),
    path('<int:pk>/entry/delete/', prompts.PromptEntryDeleteView.as_view(), name='prompt-entry-delete'),
]
