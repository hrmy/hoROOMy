from django.shortcuts import render, redirect
from .models import Ad, Flat, Metro, Image
from .forms import SearchAdsForm


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

            if form.cleaned_data.get('type'):
                ads = ads.filter(flat__type=form.cleaned_data.get('type'))

            if form.cleaned_data.get('room_num'):
                room_num = form.cleaned_data.get('room_num')
                ads = ads.filter(flat__rooms=room_num)

            if form.cleaned_data.get('metro'):
                metros = [Metro.objects.get(id=int(i)+1) for i in form.cleaned_data.get('metro')]
                ads = list(dict.fromkeys(ads.filter(flat__metros__in=metros)).keys())

            ads = list(reversed(ads))[:30]
    else:
        form = SearchAdsForm()
        ads = list(reversed(Ad.objects.all()))[:30]
    return render(request, 'core/ads.html', locals())


def ad_detail(request, ad_id):
    ad = Ad.objects.get(id=ad_id)
    images = Image.objects.filter(ad=ad)
    coords = str(ad.flat.location.lat).replace(',', '.') + "," + str(ad.flat.location.lon).replace(',', '.')
    return render(request, 'core/ad_detail.html', locals())