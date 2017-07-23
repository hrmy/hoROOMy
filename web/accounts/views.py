from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import Http404
from .forms import *


# Регистрация. Все стандартно, кроме кастомной верификации
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            key = Verification.set(user, Verification.REG)
            user.save()

            subject = 'Активация аккаунта'
            confirm_url = request.scheme + '://' + request.get_host() + reverse('register-confirm', kwargs={'key': key})
            message = render_to_string('accounts/register_mail.html', context={'url': confirm_url})
            user.send_mail(subject, message)
            return render(request, 'accounts/verify_sent.html', locals())
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', locals())


# Запрос на восстановление аккаунта. Аналогично регистрации, основное веселье в форме
def restore(request):
    if request.method == 'POST':
        form = UserRestoreForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            key = Verification.set(user, Verification.PASS)
            user.save()

            subject = 'Восстановление аккаунта'
            confirm_url = request.scheme + '://' + request.get_host() + reverse('restore-confirm', kwargs={'key': key})
            message = render_to_string('accounts/restore_mail.html', context={'url': confirm_url})
            user.send_mail(subject, message)
            return render(request, 'accounts/verify_sent.html', locals())
    else:
        form = UserRestoreForm()
    return render(request, 'accounts/restore.html', locals())


# Универсальная (почти) вьюха подтверждения/восстановления
# Проверяет ключик, в случае неудачи кидает на 404, в удачном - на установку пароля
def confirm(request, key, vn_action=None, template=None):
    user = Verification.check(key, vn_action)
    if not user: raise Http404
    if request.method == 'POST':
        form = PasswordSetForm(request.POST)
        if form.is_valid():
            Verification.reset(user)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            return render(request, template, locals())
    else:
        form = PasswordSetForm()
    return render(request, 'accounts/password_set.html', locals())


# Вьюха для личного кабинета, в качестве обратной связи - фреймворк messages (при желании можно убрать)
@login_required
def edit_account(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлен')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'accounts/edit.html', locals())


# Изменение пароля, фреймворк messages
@login_required
def edit_password(request):
    if request.method == 'POST':
        form = PasswordEditForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Чтобы не выкидывать пользователя из сессии
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно обновлен')
        else:
            messages.error(request, 'Ошибка при обновлении пароля')
    else:
        form = PasswordEditForm(request.user)
    return render(request, 'accounts/password_edit.html', locals())