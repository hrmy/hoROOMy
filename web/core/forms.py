from django import forms
from parsers.models import *

class SearchAdsForm(forms.Form):
    type = forms.ChoiceField(label='Тип',choices=[(str(i), x) for i, x in enumerate(['Квартира', 'Комната', 'Кровать'])])
    price_from = forms.IntegerField(label='Цена от', required=False)
    price_to = forms.IntegerField(label='Цена до', required=False)
    room_num = forms.IntegerField(label='Количество комнат', required=False)
    metro = forms.ModelChoiceField(queryset=Metro.objects.all(), empty_label='Выберите значение', required=False, label='Метро')

    def clean_price(self):
        if self.cleaned_data['price_from'] > self.cleaned_data['price_to']:
            raise forms.ValidationError('Введите корректный диапазон цен')
        return self.cleaned_data['price_from'], self.cleaned_data['price_to']
