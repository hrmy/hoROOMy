from django.db import models
from annoying.fields import AutoOneToOneField
from horoomy.parsers.models import Parser


class Location(models.Model):
    lat = models.FloatField('latitude', null=True, blank=True)
    lon = models.FloatField('longitude', null=True, blank=True)
    address = models.CharField('address', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return 'Location "{}"'.format(self.address or (self.lat, self.lon))


class Metro(models.Model):
    location = AutoOneToOneField(Location, null=True)
    name = models.CharField('name', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = 'Metro'
        verbose_name_plural = 'Metros'

    def __str__(self):
        return 'Metro "{}"'.format(self.name)


class Flat(models.Model):
    FLAT, ROOM, BED = map(str, range(3))
    TYPE_CHOICES = {FLAT: 'Flat', ROOM: 'Room', BED: 'Bed'}
    type = models.CharField('type', max_length=1, choices=TYPE_CHOICES.items(), default=FLAT)

    location = models.OneToOneField(Location, null=True)
    area = models.FloatField('area', null=True, blank=True)
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
    name = models.CharField('name', max_length=50, default='', blank=True)
    phone = models.CharField('phone', max_length=50, default='', blank=True)
    email = models.EmailField('email', default='', blank=True)
    vk = models.URLField('vkontakte url', default='', blank=True)
    fb = models.URLField('facebook url', default='', blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Contacts'

    def __str__(self):
        return 'Contacts for {}'.format(self.name)


class Ad(models.Model):
    OWNER, RENTER = map(str, range(2))
    TYPE_CHOICES = {OWNER: 'Owner Ad', RENTER: 'Renter Ad'}
    type = models.CharField('type', max_length=1, choices=TYPE_CHOICES.items(), default='0')

    created = models.DateTimeField('date created', null=True, blank=True)
    received = models.DateTimeField('date received', auto_now_add=True)
    parser = models.ForeignKey(Parser, null=True, blank=True, related_name='ads')
    raw = models.BooleanField('raw', default=True, blank=True)

    flat = models.OneToOneField(Flat, null=True, related_name='ad')
    url = models.URLField('url', default='', blank=True)
    description = models.TextField('description', max_length=1024, default='', blank=True)
    contacts = models.OneToOneField(Contacts, null=True, related_name='ad')

    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'

    def __str__(self):
        return self.TYPE_CHOICES[self.type] + ' #{}'.format(self.pk)


class Image(models.Model):
    LOCAL, REMOTE = map(str, range(2))
    TYPE_CHOICES = {LOCAL: 'Local image', REMOTE: 'Remote image'}
    type = models.CharField('type', max_length=1, choices=TYPE_CHOICES.items(), default='0')
    url = models.URLField('remote url', default='', blank=True)
    image = models.ImageField('local image', upload_to='images/')
    ad = models.ForeignKey(Ad, related_name='images')

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def __str__(self):
        return self.TYPE_CHOICES[self.type]
