from celery import shared_task
from horoomy.utils.logger import Logger, TgBot
from horoomy.core.models import Ad
from horoomy.utils.loader import load_package
from annoying.functions import get_object_or_None
from .models import Parser
from . import sites


@shared_task(name='parsers.clear_duplicates')
def clear_duplicates():
    logger = Logger()
    logger.name = 'Clear'
    logger.timestamp('clear')
    logger.info('Clearing duplicates...')
    count = 0
    for ad in Ad.objects.all():
        if not ad.description: continue
        qs = Ad.objects.filter(description=ad.description).exclude(id=ad.id)
        count += len(qs)
        qs.delete()
    delta = logger.timestamp('clear')
    logger.info('Succeed in {:.3f} seconds'.format(delta.seconds))
    logger.info('Total duplicates removed: {}'.format(count))
    if count: TgBot.send(logger.get_text())


parser_tasks = {}

# Проверка на существование таблицы в БД
try:
    list(Parser.objects.all())
except:
    pass
else:
    for name, task in load_package(sites, 'parse', sites.utils.wrap):
        parser_tasks[task.name] = task
        # TODO: FIX PARSER MODEL
        if get_object_or_None(Parser, name=task.name) is None:
            Parser.objects.create(name=task.name)