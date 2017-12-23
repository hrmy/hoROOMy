from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^upload/$', document_upload, name='upload'),
    url(r'^list-all/$', documents_list, name='list-all'),
    url(r'^download/(?P<id>.+)/$', document_download, name='download'),
    url(r'^document/(?P<id>.+)/$', document, name='document'),
    url(r'^open/(?P<id>.+)/$', document_open, name='open'),
]