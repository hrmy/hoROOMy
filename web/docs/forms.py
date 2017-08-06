from django import forms


class InitialsForm(forms.Form):
    second_name = forms.CharField(max_length=255, label='Фамилия')
    name = forms.CharField(max_length=255, label='Имя')
    third_name = forms.CharField(max_length=255, label='Отчество')

    def get_full_name(self):
        cd = self.cleaned_data
        return ' '.join(map(str.title, (cd['second_name'], cd['name'], cd['third_name'])))

class PassportForm(forms.Form):
    series = forms.RegexField('^[\d]{4}$', label='Серия', initial=1234)
    number = forms.RegexField('^[\d]{6}$', label='Номер', initial=123456)
    made_by = forms.CharField(max_length=255, label='Выдан', initial='отделом УФМС России по гор. Москве')
    address = forms.CharField(max_length=255, label='Зарегистрирован по адресу', initial='г. Москва, ул. Ленина, д. 1')


class RentForm(forms.Form):
    start = forms.DateField(label='Начало', widget=forms.SelectDateWidget)
    end = forms.DateField(label='Окончание', widget=forms.SelectDateWidget)
    deposit = forms.IntegerField(1000000, 0, label='Сумма залога')

    def clean_end(self):
        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            raise forms.ValidationError('Введите корректный временной промежуток')
        return self.cleaned_data['end']