from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import Http404
from .forms import *
from .tasks import send_mail


# Регистрация. Все стандартно, кроме кастомной верификации
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            Verification.set(user, Verification.REG)
            user.save()
            send_mail.delay(user.id, 'register_mail', request.scheme, request.get_host())

            return render(request, 'accounts/mail_sent.html', locals())
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', locals())


# Запрос на восстановление аккаунта. Аналогично регистрации, основное веселье в форме
def restore(request):
    if request.method == 'POST':
        form = UserRestoreForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            Verification.set(user, Verification.PASS)
            user.save()
            send_mail.delay(user.id, 'restore_mail', request.scheme, request.get_host())

            return render(request, 'accounts/mail_sent.html', locals())
    else:
        form = UserRestoreForm()
    return render(request, 'accounts/restore.html', locals())


# Универсальная (почти) вьюха подтверждения/восстановления
# Проверяет ключик, в случае неудачи кидает на 404, в удачном - на установку пароля
def confirm(request, key, vn_action=None, template_name=None):
    user = Verification.check(key, vn_action)
    if not user: raise Http404
    if request.method == 'POST':
        form = PasswordSetForm(request.user, request.POST)
        if form.is_valid():
            Verification.reset(user)
            user.set_password(form.cleaned_data.get('new_password1'))
            user.is_active = True
            user.save()

            return render(request, template_name, locals())
    else:
        form = PasswordSetForm(request.user)
    return render(request, 'accounts/password_set.html', locals())


# Вьюха личного кабинета
@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        sn_form = SocialNetworksForm(request.POST, instance=request.user.social_networks)
        if sn_form.is_valid() and user_form.is_valid():
            user_form.save()
            sn_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
    else:
        user_form = UserProfileForm(instance=request.user)
        sn_form = SocialNetworksForm(instance=request.user.social_networks)
    return render(request, 'accounts/profile.html', locals())


# Изменение пароля
@login_required
def edit_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Чтобы не выкидывать пользователя из сессии
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно обновлен')
        else:
            messages.error(request, 'Ошибка при обновлении пароля')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accounts/password_edit.html', locals())

@login_required
def creditals(request):
    user = request.user
    isSetPassword = False
    print(user.check_password(user.password))
    if user.email:
        if not user.check_password(user.password):
            isSetPassword = True
        else:
            return redirect('/')
    if request.method == 'POST':
        if isSetPassword:
            form = PasswordSetForm(request.user, request.POST)
        else:
            form = EmailAndPasswordSetForm(request.user, request.POST)
        if form.is_valid():
            if not isSetPassword:
                user.email = form.cleaned_data.get('email')
            user.set_password(form.cleaned_data.get('new_password1'))
            user.save()
            return redirect('/')
    else:
        if isSetPassword:
            form = PasswordSetForm(request.user)
        else:
            form = EmailAndPasswordSetForm(request.user)

    return render(request, 'accounts/password_set.html', locals())
