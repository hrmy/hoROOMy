from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('horoomy.accounts.urls')),
    url(r'^', include('horoomy.core.urls')),
    url(r'^docs/', include('horoomy.docs.urls')),
]
