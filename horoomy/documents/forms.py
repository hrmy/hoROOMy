from django import forms
from .models import *


class DocumentSendForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('comment', 'document')
        labels = {
            'comment': 'Комментарий',
            'document': 'Документ',
        }


class ContractForm(forms.Form):

    #Renter
    renter_first_name = forms.CharField(label='Имя', required=True)
    renter_second_name = forms.CharField(label='Фамилия', required=True)
    renter_patronymic = forms.CharField(label='Отчество', required=True)
    renter_passport_series = forms.CharField(label='Серия паспорта', required=True)
    renter_passport_number = forms.CharField(label='Номер паспорта', required=True)

    #Landlord
    landlord_first_name = forms.CharField(label='Имя', required=True)
    landlord_second_name = forms.CharField(label='Фамилия', required=True)
    landlord_patronymic = forms.CharField(label='Отчество', required=True)
    landlord_passport_series = forms.CharField(label='Серия паспорта', required=True)
    landlord_passport_number = forms.CharField(label='Номер паспорта', required=True)

    #Contract
    type = forms.CharField(label='Тип недвижимости', required=True)
