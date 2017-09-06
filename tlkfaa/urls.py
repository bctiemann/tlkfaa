from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from fanart import views as fanart_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', fanart_views.HomeView.as_view(), name='home'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
