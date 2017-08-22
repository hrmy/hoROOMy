from celery import shared_task
from horoomy.utils.logger import Logger
from horoomy.core.models import Ad
from horoomy.utils.loader import load_package
from horoomy.utils.models import table_exists
from annoying.functions import get_object_or_None
from .models import Parser
from .utils import wrap
from . import sites


@shared_task(name='parsers.clear_duplicates')
def clear_duplicates():
    logger = Logger()
    logger.name = 'Clear'
    logger.timestamp('clear')
    logger.status('Clearing duplicates...')
    count = 0
    for ad in Ad.objects.all():
        if not ad.description: continue
        qs = Ad.objects.filter(description=ad.description).exclude(id=ad.id)
        count += len(qs)
        qs.delete()
    delta = logger.timestamp('clear')
    logger.status('Succeed in {:.3f} seconds'.format(delta.seconds))
    logger.status('Total duplicates removed: {}'.format(count))
    if count: logger.report('Clear Duplicates Task')


# Проверка на существование таблицы в БД
if table_exists('parsers_parser'):
    for name, task in load_package(sites, 'parse', wrap):
        # TODO: FIX PARSER MODEL
        if get_object_or_None(Parser, name=name) is None:
            Parser.objects.create(name=name)