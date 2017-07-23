from django.conf.urls import url, include
from django.shortcuts import render

# Мега-костыль для а-ля статических страниц. В принципе, работает неплохо.
urlpatterns = [
    url(r'^$', lambda r: render(r, 'core/home.html'), name='home'),
    url(r'^ads/$', lambda r: render(r, 'core/ads.html', {'section': 'ads'}), name='ads'),
    url(r'^faq/$', lambda r: render(r, 'core/faq.html', {'section': 'faq'}), name='faq'),
    url(r'^contacts/$', lambda r: render(r, 'core/contacts.html', {'section': 'contacts'}), name='contacts'),
]