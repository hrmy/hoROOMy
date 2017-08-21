from django.db import models
from horoomy.utils.models import Choices
from .settings import *


class Proxy(models.Model):
    TYPES = Choices('HTTP', 'HTTPS', ('Both', 'HTTP / HTTPS'))
    type = models.CharField('type', max_length=1, choices=TYPES)
    address = models.CharField('address', max_length=30, unique=True)
    speed = models.PositiveSmallIntegerField('speed')
    stability = models.PositiveSmallIntegerField('stability')
    rating = models.PositiveSmallIntegerField('rating', editable=False)

    class Meta:
        verbose_name = 'Proxy'
        verbose_name_plural = 'Proxies'
        ordering = ('-rating',)

    def __str__(self):
        return '{} Proxy ({})'.format(self.TYPES[self.type], self.address)

    def save(self, **kwargs):
        self.rating = self.speed * PROXY_SPEED_RATIO
        self.rating += self.stability * PROXY_STABILITY_RATIO
        super(Proxy, self).save(**kwargs)


class UserAgent(models.Model):
    value = models.CharField('value', max_length=512)