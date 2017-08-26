from django.shortcuts import render, redirect
from .models import Ad, Flat, Metro, Image
from .forms import SearchAdsForm


def ads(request):
    if request.method == 'POST':
        form = SearchAdsForm(request.POST)
        if form.is_valid():
            qs = Ad.objects.all().select_related('flat')
            if form.cleaned_data.get('price_from') and form.cleaned_data.get('price_to'):
                price_from, price_to = form.clean_price()
                qs = qs.filter(flat__cost__lte=price_to, flat__cost__gte=price_from)
            elif form.cleaned_data.get('price_from'):
                price_from = form.cleaned_data.get('price_from')
                qs = qs.filter(flat__cost__gte=price_from)
            elif form.cleaned_data.get('price_to'):
                price_to = form.cleaned_data.get('price_to')
                qs = qs.filter(flat__cost__lte=price_to)

            if form.cleaned_data.get('type'):
                qs = qs.filter(flat__type=form.cleaned_data.get('type'))

            if form.cleaned_data.get('room_num'):
                room_num = form.cleaned_data.get('room_num')
                qs = qs.filter(flat__rooms=room_num)

            if form.cleaned_data.get('metro'):
                metros = [Metro.objects.get(pk=i) for i in form.cleaned_data.get('metro')]
                if len(metros) == 1:
                    closest = metros[0].get_closest(radius=3)
                    metros.extend(closest)
                qs = list(dict.fromkeys(qs.filter(flat__metros__in=metros)).keys())

            qs = list(reversed(qs))[:30]
    else:
        form = SearchAdsForm()
        qs = list(reversed(Ad.objects.all()))[:30]
    return render(request, 'core/ads.html', {'form': form, 'ads': qs})


def ad_details(request, ad_id):
    ad = Ad.objects.get(id=ad_id)
    images = Image.objects.filter(ad=ad)
    coords = str((ad.flat.location.lat, ad.flat.location.lon))[1:-1]
    return render(request, 'core/ad_details.html', locals())