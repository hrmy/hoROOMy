from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from horoomy.parsers.models import Ad, Flat
from .forms import *


def ads(request):
    if request.method == 'POST':
        form = SearchAdsForm(request.POST)
        if form.is_valid():
            ads = Ad.objects.all()

            if form.cleaned_data.get('price_from') and form.cleaned_data.get('price_to'):
                price_from, price_to = form.clean_price()
                ads = ads.filter(flat__cost__lte=price_to, flat__cost__gte=price_from)
            elif form.cleaned_data.get('price_from'):
                price_from = form.cleaned_data.get('price_from')
                ads = ads.filter(flat__cost__gte=price_from)
            elif form.cleaned_data.get('price_to'):
                price_to = form.cleaned_data.get('price_to')
                ads = ads.filter(flat__cost__lte=price_to)

            if form.cleaned_data.get('room_num'):
                room_num = form.cleaned_data.get('room_num')
                ads = ads.filter(flat__rooms=room_num)
            if form.cleaned_data.get('metro'):
                ads = ads.filter(flat__metros=form.cleaned_data.get('metro'))
            if form.cleaned_data.get('type'):
                ads = ads.filter(flat__type=form.cleaned_data.get('type'))

            ads = list(reversed(ads))[:30]
    else:
        form = SearchAdsForm()
        ads = list(reversed(Ad.objects.all()))[:30]
    return render(request, 'core/ads.html', locals())