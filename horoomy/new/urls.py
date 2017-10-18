from django.conf.urls import url
from django.shortcuts import render

urlpatterns = [
    url(r'^$', lambda r: render(r, 'root/home.html')),
    url(r'^robots.txt$', lambda r: render(r, 'root/robots.txt')),
    url(r'^sitemap.xml$', lambda r: render(r, 'root/sitemap.xml')),
]
