from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from django.core.validators import URLValidator
from annoying.fields import AutoOneToOneField


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
        data = {'is_superuser': True, 'is_staff': True, 'name': 'Admin', 'second_name': 'Admin'}
        extra_fields.update(data)
        return self._create_user(email, password, **extra_fields)


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


USER_ROLE_CHOICES = [
    ('0', 'Владелец'),
    ('1', 'Арендатор'),
]


# Кастомная моделька пользователя. Аналогична AbstractUser'у из django.contrib.auth.models
# См: https://github.com/django/django/blob/master/django/contrib/auth/models.py#L288
class User(AbstractBaseUser, PermissionsMixin):
    # Стандартные поля (password уже наследован)
    role = models.CharField('role', choices=USER_ROLE_CHOICES, default='0', blank=False, max_length=10)
    email = models.EmailField('email', unique=True)
    name = models.CharField('name', max_length=128, blank=False)
    second_name = models.CharField('second_name', max_length=128, blank=False, default=None)
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
        verbose_name = 'Юзер'
        verbose_name_plural = 'Юзеры'

    def __str__(self):
        return self.email

    # Где-то вызываются админом или чем-нибудь еще. Короче нужны
    get_full_name = get_short_name = lambda self: self.name


# Модель соц сетей
class SocialNetworks(models.Model):
    user = AutoOneToOneField(User, blank=True, default=None, null=True, related_name='social_networks')
    vk = models.CharField(validators=[URLValidator()], max_length=128, blank=True, default=None, null=True)
    fb = models.CharField(validators=[URLValidator()], max_length=128, blank=True, default=None, null=True)
    tw = models.CharField(validators=[URLValidator()], max_length=128, blank=True, default=None, null=True)
    go = models.CharField(validators=[URLValidator()], max_length=128, blank=True, default=None, null=True)

    class Meta:
        verbose_name = 'Cоцcети юзера'
        verbose_name_plural = 'Cоцcети юзеров'

    def __str__(self):
        return str(self.user) + '\'s Social Networks'
