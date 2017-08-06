from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from .models import *


# Форма регистрации
class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'second_name', 'role')
        labels = {
            'email': 'Email',
            'name': 'Имя',
            'second_name': 'Фамилия',
            'role': 'Кто вы?'
        }


# Форма восстановления аккаунта
class UserRestoreForm(forms.Form):
    email = forms.EmailField(label='Ваш email')

    # Различные проверки
    def clean_email(self):
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except models.ObjectDoesNotExist:
            raise forms.ValidationError('Пользователя с таким email\'ом не существует')
        if user.vn_action == Verification.REG:
            raise forms.ValidationError('Этот пользователь еще не активировал свой аккаунт')
        if user.vn_action == Verification.PASS and Verification.check(user.vn_key, user.vn_action):
            raise forms.ValidationError('Запрос на восстановление уже отправлен')
        self.cleaned_data['user'] = user
        return self.cleaned_data['email']


class PasswordSetForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)


# Форма личного кабинета (минимальный вариант)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'second_name', 'phone')
        labels = {
            'name': 'Имя',
            'second_name': 'Фамилия',
            'phone': 'Телефон'
        }


# Форма социальных сетей
class SocialNetworksForm(forms.ModelForm):
    class Meta:
        model = SocialNetworks
        fields = ('vk', 'fb', 'tw', 'go')
        labels = {
            'vk': 'Вконтакте',
            'fb': 'FaceBook',
            'tw': 'Twitter',
            'go': 'Google'
        }

class EmailAndPasswordSetForm(SetPasswordForm):
    email = forms.EmailField(label='Email')
    new_password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)