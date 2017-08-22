from celery import shared_task
from horoomy.utils.logger import Logger
from .models import Proxy
from .settings import PROXY_INITIAL_STABILITY
from traceback import format_exc


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