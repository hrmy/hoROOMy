from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ad, Flat
from .forms import *

@login_required
def ads(request):
    if request.method == 'POST':
        form = SearchAdsForm(request.POST)
        if form.is_valid():
            ads = Flat.objects.all()

            if form.cleaned_data.get('price_from') and form.cleaned_data.get('price_to'):
                price_from, price_to = form.clean_price()
                ads = ads.filter(cost__lte=price_to, cost__gte=price_from)
            elif form.cleaned_data.get('price_from'):
                price_from = form.cleaned_data.get('price_from')
                ads = ads.filter(cost__gte=price_from)
            elif form.cleaned_data.get('price_to'):
                price_to = form.cleaned_data.get('price_to')
                ads = ads.filter(cost__lte=price_to)


            if form.cleaned_data.get('room_num'):
                room_num = form.cleaned_data.get('room_num')
                ads = ads.filter(rooms=room_num)
            if form.cleaned_data.get('metro'):
                ads = ads.filter(metros=form.cleaned_data.get('metro'))
            if form.cleaned_data.get('type'):
                ads = ads.filter(type=form.cleaned_data.get('type'))

            ads = list(reversed(ads))
    else:
        form = SearchAdsForm()
        ads = list(reversed(Flat.objects.all()))[:4]
    return render(request, 'core/ads.html', locals())
