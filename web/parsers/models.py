from django.db import models

class Parser(models.Model):
    name = models.CharField('name', max_length=50, primary_key=True)
    max_price = models.PositiveIntegerField('max_price', default=50000)

    class Meta:
        verbose_name = 'Parser'
        verbose_name_plural = 'Parsers'

    def __str__(self):
        return '{} parser'.format(self.name.title())

    def get_config(self):
        return {'max_price': self.max_price}

class Flat(models.Model):
    cost = models.FloatField('cost')

    class Meta:
        verbose_name = 'Flat'
        verbose_name_plural = 'Flats'

    def __str__(self):
        return '${} Flat'.format(self.cost)