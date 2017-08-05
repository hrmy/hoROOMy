from django.utils.timezone import now, make_aware, get_current_timezone
from ..models import *
from io import StringIO
from sys import stdout
from traceback import format_exc
import requests
import re


class TgBot:
    URL = 'https://api.telegram.org/bot{token}/sendMessage'
    TOKEN = '394409524:AAHkv2WTjrHig7RouUOQAAVdZ5TgVlQOgPs'
    CHAT_ID = -227813278

    @staticmethod
    def send(text):
        url = TgBot.URL.format(token=TgBot.TOKEN)
        return requests.post(url, data={'chat_id': TgBot.CHAT_ID, 'text': text})


class Logger:
    FORMAT = '{time} [{name:^10}] {level}: {message}'
    TIME_FORMAT = '%H:%M:%S'
    INFO, WARNING, ERROR = range(3)
    LEVEL_NAMES = {
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR',
    }
    DEFAULT_NAME = 'Logger'
    CHECK_MESSAGE = 'Check "{name}" failed'
    CHECK_KEY_MESSAGE = 'Key "{key}" not found in "{name}"'
    EXTRA_STREAMS = (stdout,)

    def __init__(self, *streams):
        self.streams = [StringIO()]
        self.streams.extend(self.EXTRA_STREAMS)
        self.streams.extend(streams)
        self.name = self.DEFAULT_NAME
        self.timestamps = {}
        self.timestamp('started')
        self.log('Log session started on {}'.format(now().strftime('%d.%m.%Y')))

    def log(self, *objects, name=None, level=INFO):
        name = name or self.name
        time = now().strftime(self.TIME_FORMAT)
        level = self.LEVEL_NAMES[level]
        message = ' '.join(map(str, objects))
        if '\n' in message:
            test_string = self.FORMAT.format(time=time, name=name, level=level, message='')
            shift = len(test_string) - 3
            message = ('\n...' + ' ' * shift).join(message.split('\n'))
        string = self.FORMAT.format(time=time, name=name, level=level, message=message)
        for s in self.streams: print(string, file=s)

    def check(self, expression, level=WARNING, name='unnamed check'):
        if not expression:
            self.log(self.CHECK_MESSAGE.format(name=name), level=level)
        return expression

    def check_keys(self, dict, *keys, level=WARNING, name='unnamed dict'):
        for key in keys:
            if key not in dict:
                self.log(self.CHECK_KEY_MESSAGE.format(key=key, name=name), level=level)

    def timestamp(self, key):
        if key in self.timestamps:
            delta = now() - self.timestamps[key]
            self.timestamps[key] = now()
            return delta
        self.timestamps[key] = now()

    get_text = lambda self: self.streams[0].getvalue()
    close = lambda self: self.streams[0].close()
    info = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.INFO)
    warning = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.WARNING)
    error = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.ERROR)


def trim(s):
    if not s or not isinstance(s, str): return ''
    words = filter(None, re.split('\s', s))
    return ' '.join(words)


def try_default(func, value, default=None):
    try:
        return func(value)
    except:
        return default


def clean(data, logger):
    logger.name = 'Clean'
    logger.info('Cleaning data...')
    logger.timestamp('clean')
    clean_data = {}

    # Metros
    logger.check_keys(data, 'metro', name='data')
    raw_metros = [trim(i).lower() for i in data.get('metro', [])]
    clean_data['metros'] = list(filter(None, raw_metros))

    # Flat location
    logger.check_keys(data, 'loc', 'adr', name='data')
    clean_data['address'] = trim(data.get('adr', ''))
    clean_data['lat'] = None
    clean_data['long'] = None
    raw_loc = data.get('loc', None)
    if isinstance(raw_loc, str): raw_loc = trim(raw_loc.split(','))
    if isinstance(raw_loc, list) or isinstance(raw_loc, tuple):
        try:
            lat = try_default(float, raw_loc[1])
            long = try_default(float, raw_loc[0])
            if lat and long:
                clean_data['lat'] = lat
                clean_data['long'] = long
        except:
            logger.warning('Invalid "loc" in "data": {}'.format(raw_loc))

    # Flat
    logger.check_keys(data, 'cost', 'area', 'room_num', name='data')
    clean_data['cost'] = try_default(float, data.get('cost'))
    clean_data['area'] = try_default(float, data.get('area'))
    clean_data['rooms'] = None
    raw_rooms = try_default(int, data.get('room_num'))
    if raw_rooms == -1:
        clean_data['flat_type'] = Flat.BED
    elif raw_rooms == 0:
        clean_data['flat_type'] = Flat.ROOM
    else:
        clean_data['flat_type'] = Flat.FLAT
        clean_data['rooms'] = raw_rooms

    # Contacts
    logger.check_keys(data, 'contacts', name='data')
    clean_data['contacts'] = dict.fromkeys(('name', 'phone', 'vk', 'fb'), '')
    raw_contacts = data.get('contacts', None)
    if raw_contacts:
        logger.check_keys(raw_contacts, 'person_name', 'phone', name='contacts')
        clean_data['contacts']['name'] = trim(raw_contacts.get('person_name'))
        clean_data['contacts']['phone'] = trim(raw_contacts.get('phone'))
        clean_data['contacts']['vk'] = trim(raw_contacts.get('vk'))
        clean_data['contacts']['fb'] = trim(raw_contacts.get('fb'))

    # Ad
    logger.check_keys(data, 'url', 'descr', 'date', 'parser', 'type', name='data')
    clean_data['url'] = trim(data.get('url'))
    clean_data['description'] = trim(data.get('descr'))
    clean_data['parser'] = data.get('parser')
    clean_data['type'] = Ad.OWNER if data.get('type', 'owner') == 'owner' else Ad.RENTER
    clean_data['created'] = None
    raw_date = data.get('date')
    try:
        clean_data['created'] = make_aware(raw_date, get_current_timezone())
    except:
        logger.warning('Invalid "date" in "data": {}'.format(raw_date))

    # Images
    logger.check_keys(data, 'pics', name='data')
    clean_data['images'] = []
    raw_pics = data.get('pics')
    if isinstance(raw_pics, list) or isinstance(raw_pics, tuple):
        if all(map(lambda x: isinstance(x, str), raw_pics)):
            clean_data['images'].extend(map(trim, raw_pics))

    delta = logger.timestamp('clean')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return clean_data


def create(data, logger):
    logger.name = 'Create'
    logger.info('Creating objects...')
    # logger.info('Raw data: {}'.format(data))
    logger.timestamp('create')

    # Metros
    metros = [Metro.objects.get_or_create(name=i)[0] for i in data['metros']]

    # Flat location
    flat_location = Location(
        address=data['address'],
        lat=data['lat'],
        long=data['long']
    )
    flat_location.save()

    # Flat
    flat = Flat(
        type=data['flat_type'],
        cost=data['cost'],
        area=data['area'],
        rooms=data['rooms'],
        location=flat_location
    )
    flat.save()
    flat.metros.add(*metros)

    # Contacts
    contacts = Contacts(
        name=data['contacts']['name'],
        phone=data['contacts']['phone'],
        vk=data['contacts']['vk'],
        fb=data['contacts']['fb']
    )
    contacts.save()

    # Ad
    ad = Ad(
        type=data['type'],
        url=data['url'],
        description=data['description'],
        created=data['created'],
        parser=data['parser'],
        contacts=contacts,
        flat=flat,
    )
    ad.save()

    # Images
    images = [Image(type=Image.REMOTE, ad=ad, url=i) for i in data['images']]
    Image.objects.bulk_create(images)

    delta = logger.timestamp('create')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return ad


# Обертка на парсеры
def wrap(func, name):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    def deco():
        logger = Logger()
        logger.name = 'Wrapper'
        logger.info('Parser "{}" task initializing...'.format(name))
        parser = Parser.objects.get(name=name)
        config = parser.get_config()
        config['logger'] = logger
        logger.info('Got config: {}'.format(config))

        logger.info('Parsing...')
        logger.name = name.title()

        objects, errors, success = 0, 0, True
        try:
            for data in func(**config):
                try:
                    data['parser'] = parser
                    clean_data = clean(data, logger)
                    create(clean_data, logger)
                except:
                    logger.error('Error during data processing:\n', format_exc())
                    errors += 1
                else:
                    objects += 1
        except:
            logger.error('Unexpected error - shutting down...\n', format_exc())
            errors += 1
            success = False

        logger.name = 'Wrapper'
        delta = logger.timestamp('started')
        logger.info('Parser task succeed in {} seconds'.format(delta.seconds))
        logger.info('Total objects created: {} / {}. Warm shutdown: {}'.format(objects, objects + errors, success))
        TgBot.send(logger.get_text())

    deco.__name__ = 'parse_' + name

    return deco
