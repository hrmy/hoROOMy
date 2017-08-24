from django.db import models
from annoying.fields import AutoOneToOneField
from horoomy.parsers.models import Parser
from horoomy.utils.models import Choices
from .utils import YMapsAPI


class Location(models.Model):
    lat = models.FloatField('latitude', null=True, blank=True)
    lon = models.FloatField('longitude', null=True, blank=True)
    address = models.CharField('address', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return 'Location "{}"'.format(self.address or (self.lat, self.lon))

    # Входит ли локация other в круг с центром в данной локации и радиусом radius км.
    def is_in_circle(self, other, radius=5):
        # Пересчет километров в градусы
        radius /= 111
        distance = ((self.lat - other.lat) ** 2 + (self.lon - other.lon) ** 2) ** 0.5
        return distance if distance <= radius else False

    def evolve(self):
        try:
            geodata = YMapsAPI.get_geodata(self)
        except:
            return None
        self.lat = geodata['lat']
        self.lon = geodata['lon']
        self.address = geodata['address']
        return geodata['exact']


class Metro(models.Model):
    location = AutoOneToOneField(Location, null=True)
    name = models.CharField('name', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = 'Metro'
        verbose_name_plural = 'Metros'

    def __str__(self):
        return 'Metro "{}"'.format(self.name)

    # Получить ближайшие метро в радиусе radius км.
    def get_closest(self, radius=5):
        closest = []
        qs = Metro.objects.all().exclude(pk=self.pk).select_related('location')
        for other in qs:
            distance = other.location.is_in_circle(self.location, radius)
            if distance is not False:
                other.distance = distance
                closest.append(other)
        closest.sort(key=lambda x: x.distance)
        return closest


class Flat(models.Model):
    TYPES = Choices('Flat', 'Room', 'Bed')
    type = models.CharField('type', max_length=1, choices=TYPES, default=TYPES.FLAT)

    location = models.OneToOneField(Location, null=True)
    area = models.FloatField('area', null=True, blank=True)
    cost = models.FloatField('cost', null=True, blank=True)
    rooms = models.PositiveSmallIntegerField('rooms', null=True, blank=True)
    metros = models.ManyToManyField(Metro, related_name='flats', blank=True)

    class Meta:
        verbose_name = 'Flat'
        verbose_name_plural = 'Flats'

    def __str__(self):
        return '{} at {}'.format(self.TYPES[self.type], self.location.address)


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
        return 'Contacts ({})'.format(self.phone or self.name)


class Ad(models.Model):
    TYPES = Choices('Owner', 'Renter')
    type = models.CharField('type', max_length=1, choices=TYPES, default='0')

    created = models.DateTimeField('date created', null=True, blank=True)
    received = models.DateTimeField('date received', auto_now_add=True)
    parser = models.ForeignKey(Parser, null=True, blank=True, related_name='ads', on_delete=models.SET_NULL)
    complete = models.BooleanField('complete', default=True, blank=True)

    flat = models.OneToOneField(Flat, null=True, related_name='ad')
    url = models.URLField('url', default='', blank=True)
    description = models.TextField('description', max_length=1024, default='', blank=True)
    contacts = models.OneToOneField(Contacts, null=True, related_name='ad')

    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'

    def __str__(self):
        return self.TYPES[self.type] + ' Ad #{}'.format(self.pk)


class Image(models.Model):
    TYPES = Choices('Local', 'Remote')
    type = models.CharField('type', max_length=1, choices=TYPES, default='0')
    url = models.URLField('remote url', default='', blank=True)
    image = models.ImageField('local image', upload_to='images/', blank=True)
    ad = models.ForeignKey(Ad, related_name='images')

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def __str__(self):
        return self.TYPES[self.type] + ' Image'

