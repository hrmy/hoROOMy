from celery import shared_task
from horoomy.utils.logger import Logger, TgBot
from ..models import Proxy
from ..settings import PROXY_INITIAL_STABILITY
from traceback import format_exc


# Обертка на парсеры
def wrap(func, name=None):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    @shared_task(name='proxy.' + name)
    def deco(**config):
        logger = Logger()
        logger.name = 'Wrapper'
        logger.info('Proxy parser "{}" task initializing...'.format(name))
        logger.info('Parsing...')
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
            logger.error('Unexpected error - shutting down...\n', format_exc())
            success = False

        logger.name = 'Wrapper'
        delta = logger.timestamp('started')
        logger.info('Parser task succeed in {} seconds'.format(delta.seconds))
        logger.info('Total objects created: {}. Warm shutdown: {}'.format(objects, success))
        TgBot.send(logger.get_text())

    return deco