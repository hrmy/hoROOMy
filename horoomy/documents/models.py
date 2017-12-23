from django.db import models
from horoomy.accounts.models import User

# Create your models here.

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Document(models.Model):
    comment = models.TextField('comment', null=True, blank=True, max_length=256)
    document = models.FileField('document', upload_to=user_directory_path)
    file_extension = models.CharField('extension', max_length=32)
    user = models.ForeignKey(User)

    def save(self, *args, **kwargs):
        self.file_extension = str(self.document).split('.')[-1]
        super(Document, self).save(*args, **kwargs)

    def __str__(self):
        return 'Документ пользователя id' + str(self.user.id) + ' - #' + str(self.id)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


class Renter(models.Model):
    first_name = models.CharField(name='first_name', blank=False, null=False, max_length=128)
    patronymic = models.CharField(name='patronymic', blank=False, null=False, max_length=128)
    second_name = models.CharField(name='second_name', blank=False, null=False, max_length=128)
    passport_series = models.CharField(name='passport_series', blank=False, null=False, max_length=32)
    passport_number = models.CharField(name='passport_number', blank=False, null=False, max_length=32)

    def __str__(self):
        return 'Арендатор ' + str(self.id)

    class Meta:
        verbose_name = 'Арендатор'
        verbose_name_plural = 'Арендаторы'


class Landlord(models.Model):
    first_name = models.CharField(name='first_name', blank=False, null=False, max_length=128)
    patronymic = models.CharField(name='patronymic', blank=False, null=False, max_length=128)
    second_name = models.CharField(name='second_name', blank=False, null=False, max_length=128)
    passport_series = models.CharField(name='passport_series', blank=False, null=False, max_length=32)
    passport_number = models.CharField(name='passport_number', blank=False, null=False, max_length=32)

    def __str__(self):
        return 'Арендодатель ' + str(self.id)

    class Meta:
        verbose_name = 'Арендодатель'
        verbose_name_plural = 'Арендодатели'

class Contract(models.Model):
    type = models.CharField(name='type', blank=False, null=False, max_length=128, default='-')
    renter = models.ForeignKey(Renter, name='renter', blank=False, null=False, default=None)
    landlord = models.ForeignKey(Landlord, name='landlord', blank=False, null=False, default=None)
    document = models.ForeignKey(Document)
    created_date = models.DateTimeField('created date', auto_now_add=True)
    expiration_date = models.DateTimeField('expiration date', auto_now_add=True)

    def __str__(self):
        return 'Контракт ' + str(self.id)

    class Meta:
        verbose_name = 'Контракт'
        verbose_name_plural = 'Контракты'