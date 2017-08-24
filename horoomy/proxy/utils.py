from celery import shared_task
from horoomy.utils.logger import Logger
from .models import Proxy
from .settings import *
from annoying.functions import get_object_or_None
from traceback import format_exc
from time import time
import requests


def test_url(url, proxy):
    proxies = {'http': proxy, 'https': proxy}
    try:
        start = time()
        r = requests.get(url, timeout=PROXY_TIMEOUT, proxies=proxies)
        delta = time() - start
        if r.status_code != 200: return False
    except:
        return False
    return delta


def test_proxy(proxy):
    http = test_url(HTTP_URL, proxy)
    https = test_url(HTTPS_URL, proxy)
    if not http and not https: return None
    proxy = {'address': proxy}
    if http and https:
        proxy['type'] = Proxy.TYPES.BOTH
        speed = 2 / (http + https)
    else:
        proxy['type'] = Proxy.TYPES.HTTP if http else Proxy.TYPES.HTTPS
        speed = 1 / (http or https)
    proxy['speed'] = speed * 1000
    return proxy


# Обертка на парсеры
def wrap(func, name=None):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    @shared_task(name='parse.' + name)
    def deco(**config):
        logger = Logger().channel('Wrapper')
        logger.status('Proxy parser "{}" task initializing...'.format(name))
        logger.status('Parsing...')
        logger.name = name.title()

        objects, success = 0, True
        try:
            for data in func(**config):
                if get_object_or_None(Proxy, address=data['address']) is not None: continue
                proxy = Proxy(
                    type=data['type'],
                    address=data['address'],
                    speed=data['speed'],
                    stability=PROXY_INITIAL_STABILITY
                )
                proxy.save()
                logger.info('Saved {}'.format(proxy))
                objects += 1
        except:
            logger.status('Unexpected error - shutting down...\n', format_exc())
            success = False

        delta = logger.timestamp('started')
        logger.status('Parser task succeed in {} seconds'.format(delta.seconds))
        logger.status('Total objects created: {}. Warm shutdown: {}'.format(objects, success))
        logger.report('Proxy Parser')

    return deco