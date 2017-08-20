from django.db import models
from annoying.fields import AutoOneToOneField
from djcelery.models import PeriodicTask
from json import loads


class Parser(models.Model):
    name = models.CharField('name', max_length=50, primary_key=True)
    config = models.TextField('config', max_length=1024, default='{}', blank=False)
    task = AutoOneToOneField(PeriodicTask, blank=False, null=True)

    class Meta:
        verbose_name = 'Parser'
        verbose_name_plural = 'Parsers'

    def __str__(self):
        return '{} parser'.format(self.name.title())

    def save(self, **kwargs):
        if not self.task:
            task = PeriodicTask(name='{} Parser task'.format(self.name.title()))
            task.task = 'parsers.' + self.name
            task.enabled = False
            task.save()
            self.task = task
        models.Model.save(self, **kwargs)

    def get_config(self):
        try:
            return loads(self.config)
        except:
            return {}