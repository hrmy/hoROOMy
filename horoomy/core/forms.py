from django import forms
from horoomy.utils.models import table_exists
from .models import *

METRO_CHOICES = [(i.pk, i.name) for i in Metro.objects.all()] if table_exists('core_metro') else []


class SearchAdsForm(forms.Form):
    type = forms.ChoiceField(label='Тип', choices=Flat.TYPES)
    price_from = forms.IntegerField(label='Цена от', required=False)
    price_to = forms.IntegerField(label='Цена до', required=False)
    room_num = forms.IntegerField(label='Комнат', required=False)
    metro = forms.MultipleChoiceField(label='Метро', choices=METRO_CHOICES, widget=forms.SelectMultiple(),
                                      required=False)

    def clean_price(self):
        if self.cleaned_data['price_from'] > self.cleaned_data['price_to']:
            raise forms.ValidationError('Введите корректный диапазон цен')
        return self.cleaned_data['price_from'], self.cleaned_data['price_to']
