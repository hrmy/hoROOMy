from django.db import models
from annoying.fields import AutoOneToOneField
from phonenumber_field.modelfields import PhoneNumberField


class Parser(models.Model):
    name = models.CharField('name', max_length=50, primary_key=True)
    max_price = models.PositiveIntegerField('max_price', null=True, blank=True)

    class Meta:
        verbose_name = 'Parser'
        verbose_name_plural = 'Parsers'

    def __str__(self):
        return '{} parser'.format(self.name.title())

    def get_config(self):
        return {'max_price': self.max_price}


class Location(models.Model):
    lat = models.FloatField('latitude', null=True, blank=True)
    long = models.FloatField('longitude', null=True, blank=True)
    address = models.CharField('address', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return 'Location "{}"'.format(self.address or (self.lat, self.long))


class Metro(models.Model):
    location = AutoOneToOneField(Location, null=True)
    name = models.CharField('name', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = 'Metro'
        verbose_name_plural = 'Metros'

    def __str__(self):
        return 'Metro "{}"'.format(self.name)


class Flat(models.Model):
    TYPE_CHOICES = {'0': 'Flat', '1': 'Room', '2': 'Bed'}
    type = models.CharField('type', max_length=1, choices=TYPE_CHOICES.items(), default='0')  # Rename?
    location = AutoOneToOneField(Location, null=True)
    area = models.FloatField('square', null=True, blank=True)  # Rename?
    cost = models.FloatField('cost', null=True, blank=True)
    rooms = models.PositiveSmallIntegerField('rooms', null=True, blank=True)
    metros = models.ManyToManyField(Metro, related_name='flats', blank=True)

    class Meta:
        verbose_name = 'Flat'
        verbose_name_plural = 'Flats'

    def __str__(self):
        return '{} at {}'.format(self.TYPE_CHOICES[self.type], self.location)


# TODO: Перенести в accounts и замержить с SocialNetworks
class Contacts(models.Model):
    phone = PhoneNumberField('phone', default='', blank=True)
    email = models.EmailField('email', default='', blank=True)
    vk = models.URLField('vkontakte link', default='', blank=True)
    fb = models.URLField('facebook link', default='', blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Contacts'

    def __str__(self):
        return 'Contacts for {}'.format(self.ad)


class Ad(models.Model):
    TYPE_CHOICES = {'0': 'Owner Ad', '1': 'Renter Ad'}
    type = models.CharField('type', max_length=1, choices=TYPE_CHOICES.items(), default='0')
    created = models.DateTimeField('date created', null=True, blank=True)
    received = models.DateTimeField('date received', auto_now_add=True)
    parser = models.OneToOneField(Parser, null=True, blank=True)
    raw = models.BooleanField('raw', default=True, blank=True)

    flat = AutoOneToOneField(Flat, null=True, related_name='ad')
    link = models.URLField('link', default='', blank=True)
    description = models.CharField('description', max_length=1024, default='', blank=True)
    contacts = AutoOneToOneField(Contacts, null=True, related_name='ad')

    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'

    def __str__(self):
        return self.TYPE_CHOICES[self.type] + ' #{}'.format(self.pk)