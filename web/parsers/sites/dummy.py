from . import *

def parse(**config):
    logger = config['logger']
    logger.info('Hello from dummy parser!')
    raise Exception('Test exception')