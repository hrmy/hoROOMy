from django.db import models


class Sdam(models.Model):
    uid = models.CharField()
    price = models.IntegerField()
    room_num = models.PositiveSmallIntegerField()
    area = models.PositiveSmallIntegerField()
    phone = models.BigIntegerField()
    date = models.DateField()

    # these fields will be used to store JSON
    pics = models.TextField()
    contacts = models.TextField()
    metro = models.CharField()

    prooflink = models.URLField()
    loc = models.CharField()
    adr = models.CharField()
    fromwhere = models.CharField()
    descr = models.TextField()


