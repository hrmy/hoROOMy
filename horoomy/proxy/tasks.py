from horoomy.utils.models import table_exists
from horoomy.utils.loader import load_package
from horoomy.parsers.models import Parser
from annoying.functions import get_object_or_None
from celery import shared_task
from .utils import wrap, test_proxy
from .models import Proxy
from . import sites


@shared_task(name='proxy.testall')
def testall():
    for proxy in Proxy.objects.all():
        data = test_proxy(proxy.address)
        if not data:
            proxy.delete()
            continue
        proxy.type = data['type']
        proxy.speed = data['speed']
        proxy.save()

# Проверка на существование таблицы в БД
if table_exists('parsers_parser'):
    for name, task in load_package(sites, 'parse', wrap):
        # TODO: FIX PARSER MODEL
        if get_object_or_None(Parser, name=name) is None:
            Parser.objects.create(name=name)