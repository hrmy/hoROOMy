from django import forms
from django.contrib.auth import get_user_model
from django.db import models
from .models import Verification


# Форма регистрации
class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'name')
        labels = {
            'email': 'Email',
            'name': 'Имя'
        }


# Форма восстановления аккаунта
class UserRestoreForm(forms.Form):
    email = forms.EmailField(label='Ваш email')

    # Различные проверки
    def clean_email(self):
        try:
            user = get_user_model().objects.get(email=self.cleaned_data['email'])
        except models.ObjectDoesNotExist:
            raise forms.ValidationError('Пользователя с таким email\'ом не существует')
        if user.vn_action == Verification.REG:
            raise forms.ValidationError('Этот пользователь еще не активировал свой аккаунт')
        if user.vn_action == Verification.PASS and Verification.check(user.vn_key, user.vn_action):
            raise forms.ValidationError('Запрос на восстановление уже отправлен')
        self.cleaned_data['user'] = user
        return self.cleaned_data['email']


# Форма установки пароля (ВЕЛОСИПЕД)
# TODO: Наследовать auth.forms.SetPasswordForm и переписать сообщения об ошибках
class PasswordSetForm(forms.Form):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


# Форма изменения пароля (ВЕЛОСИПЕД)
# TODO: Наследовать auth.forms.EditPasswordForm и переписать сообщения об ошибках
class PasswordEditForm(forms.Form):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)
    password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        forms.Form.__init__(self, *args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Неверный пароль')
        return old_password

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']

    def save(self):
        password = self.cleaned_data['password']
        self.user.set_password(password)
        self.user.save()


# Форма личного кабинета (минимальный вариант)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('name', 'phone')
        labels = {
            'name': 'Имя',
            'phone': 'Телефон'
        }