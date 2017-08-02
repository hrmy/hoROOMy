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


class Renter(models.Model):
    uid = models.CharField()
    cost = models.IntegerField()
    room_num = models.PositiveSmallIntegerField()
    phone = models.BigIntegerField()
    prooflink = models.URLField()
    descr = models.TextField()
    date = models.DateField()
    fromwhere = models.CharField()

    # these fields will be used to store JSON
    pics = models.TextField()
    contacts = models.TextField()
    metro = models.CharField()


# по идее, Flat должен наследовать Renter и добавлять к уже объявленным ещё несколько полей
class Flat(Renter):
    area = models.PositiveSmallIntegerField()
    loc = models.CharField()
    adr = models.CharField()

    class Meta:
        verbose_name = 'Flat'
        verbose_name_plural = 'Flats'

    def __str__(self):
        return '${} Flat'.format(self.cost)