from django.db import models
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from templated_email import send_templated_mail


# Менеджер для кастомной модельки. Аналогичен UserManager'у из django.contrib.auth.models
# См: https://github.com/django/django/blob/master/django/contrib/auth/models.py#L131
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email: raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        # Теоретически тут должны быть проверки на is_superuser=True и is_staff=True в extra_fields
        return self._create_user(email, password, is_superuser=True, is_staff=True, **extra_fields)


# Класс для управления верификацией
class Verification:
    # Типы верификации: ОТСУТСТВУЕТ | РЕГИСТРАЦИЯ | ВОССТАНОВЛЕНИЕ
    NONE, REG, PASS = map(str, range(3))
    CHOICES = [(NONE, 'NONE'), (REG, 'REG'), (PASS, 'PASS')]

    # Установка верификации: записывает ключик, тип и срок действия
    @staticmethod
    def set(user, action):
        user.vn_action = action
        key = get_random_string(length=50)
        user.vn_key = key
        user.vn_expire = now() + timedelta(days=1)
        return key

    # Проверка верификации, в успешном случае возвращяет юзера
    @staticmethod
    def check(key, action):
        try:
            user = User.objects.get(vn_key=key)
        except models.ObjectDoesNotExist:
            return False
        if user.vn_action != action: return False
        if user.vn_expire <= now(): return False
        user.vn_action = Verification.NONE
        return user

    # Сброс верификации
    @staticmethod
    def reset(user):
        user.vn_action = Verification.NONE


# Кастомная моделька пользователя. Аналогична AbstractUser'у из django.contrib.auth.models
# См: https://github.com/django/django/blob/master/django/contrib/auth/models.py#L288
class User(AbstractBaseUser, PermissionsMixin):
    # Стандартные поля (password уже наследован)
    email = models.EmailField('email', unique=True)
    name = models.CharField('name', max_length=128, blank=False)
    # Флажки, нужные для django-admin, ну или просто полезные
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=False)
    # Поля для верификации
    vn_action = models.CharField('verification action', max_length=10, choices=Verification.CHOICES, blank=True)
    vn_key = models.CharField('verification key', max_length=50, blank=True)
    vn_expire = models.DateTimeField('verification key expire', default=None, null=True, blank=True)
    # Дополнительые поля (вынести в отдельную модель 1to1?)
    phone = PhoneNumberField('phone', null=True, blank=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    # Кастомный менеджер (зачем?)
    objects = UserManager()
    # Указатели для django-auth. В качестве логина - почта
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'юзер'
        verbose_name_plural = 'юзеры'

    # Где-то вызываются админом или чем-нибудь еще. Короче нужны
    get_full_name = get_short_name = lambda self: self.name

    # Шорткат для отправки писем
    def send_mail(self,request, from_email=None, **kwargs):
        #send_mail(subject, text_content, from_email, [self.email], fail_silently=True, html_message=html_content, **kwargs)
        send_templated_mail(
                template_prefix = 'accounts/',
                template_name = 'register_html_mail',
                template_suffix = 'html',
                from_email = from_email,
                recipient_list = [self.email],
                context = {
                    'name': self.name,
                    'host': request.get_host(),
                    'scheme': request.scheme,
                    'key': self.vn_key,
                }
            )