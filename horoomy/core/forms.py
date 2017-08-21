from django import forms
from .models import *

class SearchAdsForm(forms.Form):
    type = forms.ChoiceField(label='Тип',choices=[(str(i), x) for i, x in enumerate(['Квартира', 'Комната', 'Кровать'])])
    price_from = forms.IntegerField(label='Цена от', required=False)
    price_to = forms.IntegerField(label='Цена до', required=False)
    room_num = forms.IntegerField(label='Количество комнат', required=False)
    metro = forms.MultipleChoiceField(choices=[(str(i), x) for i, x in enumerate(Metro.objects.all())], widget=forms.SelectMultiple())

    def clean_price(self):
        if self.cleaned_data['price_from'] > self.cleaned_data['price_to']:
            raise forms.ValidationError('Введите корректный диапазон цен')
        return self.cleaned_data['price_from'], self.cleaned_data['price_to']
