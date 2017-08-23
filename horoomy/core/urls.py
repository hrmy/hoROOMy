from django.conf.urls import url
from django.shortcuts import render
from django.shortcuts import redirect
from . import views

# Мега-костыль для а-ля статических страниц. В принципе, работает неплохо.
urlpatterns = [
    url(r'^$', lambda r: redirect('home')),
    url(r'^home/$', lambda r: render(r, 'core/home.html'), name='home'),
    url(r'^faq/$', lambda r: render(r, 'core/faq.html', {'section': 'faq'}), name='faq'),
    url(r'^contacts/$', lambda r: render(r, 'core/contacts.html', {'section': 'contacts'}), name='contacts'),
    url(r'^ads/$', views.ads, name='ads'),
    url(r'^ad-detail/(?P<ad_id>[0-9]+)/$', views.ad_detail, name='ad-detail'),
]