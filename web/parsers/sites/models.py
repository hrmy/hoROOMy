from django.db import models


class Sdam(models.Model):
    uid = models.CharField()
    price = models.IntegerField()
    room_num = models.PositiveSmallIntegerField()
    area = models.PositiveSmallIntegerField()
    phone = models.BigIntegerField()
    date = models.DateField()
    prooflink = models.URLField()
    loc = models.CharField()
    adr = models.CharField()
    fromwhere = models.CharField()
    descr = models.TextField()


class Snimu(models.Model):
    uid = models.CharField()
    price = models.IntegerField()
    room_num = models.PositiveSmallIntegerField()
    phone = models.BigIntegerField()
    prooflink = models.URLField()
    descr = models.TextField()

    # these fields will be used to store JSON
    pics = models.TextField()
    contacts = models.TextField()
    metro = models.CharField()