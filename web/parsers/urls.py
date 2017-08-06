from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ads/$', views.ads, name='ads'),
]