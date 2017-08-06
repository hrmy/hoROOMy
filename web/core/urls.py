from django.conf.urls import url
from django.shortcuts import render

# Мега-костыль для а-ля статических страниц. В принципе, работает неплохо.
urlpatterns = [
    url(r'^$', lambda r: render(r, 'core/home.html'), name='home'),
    url(r'^faq/$', lambda r: render(r, 'core/faq.html', {'section': 'faq'}), name='faq'),
    url(r'^contacts/$', lambda r: render(r, 'core/contacts.html', {'section': 'contacts'}), name='contacts'),
]