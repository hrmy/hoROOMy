import re
import sys
import hashlib
from . import *
from models import *
from traceback import format_tb

from annoying.functions import get_object_or_None
from ..models import *


# ---------------------------------------TELEGRAM BOT UTIL----------------------------------------------
class Bot:
    full_link = ""

    def __init__(self, chat_id):
        self.full_link = "https://api.telegram.org/bot332143024:AAFXvkc397uXcvN3HgbiKQ0GTaNXKf-H-zs/%s?chat_id="+chat_id

    def sendMessage(self, text):
        requests.post(self.full_link % 'sendMessage', data={'text': text})

# since we use only one bot, here are its params
ERROR_CHAT_ID = '273633310'
alertBot = Bot(ERROR_CHAT_ID)


# alerting an exception occured with the bot
def alertExc():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    Bot(ERROR_CHAT_ID).sendMessage(str(format_tb(exc_traceback)) + str(exc_value) + str(exc_type))

# -------------------------------------------PROCESSING JSON-------------------------------------------

def evolve(data):

    # get coordinates if we know address
    def get_loc(adr):
        api_adr = adr.replace(' ', '+')
        url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % api_adr
        loc = requests.get(url).text
        loc = json.loads(loc)
        loc = loc['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]['pos']
        loc = list(loc.split(" "))
        #loc = loc[1] + "," + loc[0]
        print("!!!GET_LOC USED!!!")
        return loc

    # get address if we know coordinates
    def get_adr(loc):
        if loc is not None:
            loc_str = loc[1] + "," + loc[0]
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % loc
            adr = requests.get(url).text
            adr = json.loads(adr)
            print("!!!GET_ADR USED!!!")
            return adr['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']


    # Filter flats -- phone and address should be given
    if data['adr'] is None:
        print("""-----REMOVED FOR NO ADR GIVEN -----""")
        return {'error': 'adress not given'}

    if data['contacts']['phone'] is None:
        print("""-----REMOVED FOR NO ADR GIVEN -----""")
        return {'error': 'phone not given'}
    else:   # turn the phone into an integer
        data['contacts']['phone'] = int(re.sub("\+7|\s|-|\(|\)|^8|^7", "", data['contacts']['phone']))


    # getting loc and adr
    if (data['loc'] is None):
        try:
            data["loc"] = get_loc(data["adr"])
        except:
            data['loc'] = "YANDEXLOCERR"
            print('YANDEXLOCERR')

    elif (data['adr'] == "") or (data['adr'] is None):
        try:
            data["adr"] = get_adr(data["loc"])
        except:
            data['adr'] = 'YANDEXADRERR'
            print("YANDEXADRERR")

    data['uid'] = str(hashlib.md5(data['descr'].encode('utf-8')).hexdigest())

# --------------------------SPLITTING THE JSON INTO MODELS-----------------------------

# ------------------------------------- LOGGER ----------------------------------------

from io import StringIO
from sys import stdout
from django.utils.timezone import now


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
        if expression:
            self.log(self.CHECK_MESSAGE.format(name=name), level=level)
        return expression

    def check_keys(self, dict, *keys, level=WARNING, name='unnamed dict'):
        for key in keys:
            test = key in dict
            if not test:
                self.log(self.CHECK_KEY_MESSAGE.format(key=key, name=name), level=level)
            yield test

    get_text = lambda self: self.streams[0].getvalue()
    close = lambda self: self.streams[0].close()
    info = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.INFO)
    warning = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.WARNING)
    error = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.ERROR)


# --------------------------SPLITTING THE JSON INTO MODELS-----------------------------

def create(data, logger):
    logger.info('Creating object...')
    start_time = now()

    # Metros
    logger.check_keys(data, 'metro', name='data')
    raw_metros = data.get('metro', [])
    metros = [Metro.objects.get_or_create(name=i.lower())[0] for i in raw_metros]
    logger.check(not metros, name='no metros')

    # Flat location
    logger.check_keys(data, 'loc', 'adr', name='data')
    raw_loc = data.get('loc', (None, None))
    flat_location = Location(
        address=data.get('adr', ''),
        lat=raw_loc[1],
        long=raw_loc[0]
    )
    logger.check_keys(data, 'adr', name='data')
    flat_location.save()

    # Flat
    logger.check_keys(data, 'cost', 'area', 'room_num', name='data')
    flat = Flat(
        cost=data.get('cost', None),
        area=data.get('area', None)
    )
    raw_rooms = data.get('room_num', None)
    if raw_rooms == -1:
        flat.type = Flat.BED
    elif raw_rooms == 0:
        flat.type = Flat.ROOM
    else:
        flat.type = Flat.FLAT
        flat.rooms = raw_rooms
    flat.location = flat_location
    flat.save()
    flat.metros.add(*metros)

    # Contacts
    logger.check_keys(data, 'contacts', name='data')
    raw_contacts = data.get('contacts', {})
    if raw_contacts:
        logger.check_keys(raw_contacts, 'phone', 'vk', 'fb', name='contacts')
    contacts = Contacts(
        phone=raw_contacts.get('phone', ''),
        vk=raw_contacts.get('vk', ''),
        fb=raw_contacts.get('fb', '')
    )
    contacts.save()

    # Ad
    logger.check_keys(data, 'url', 'descr', 'date', 'type', name='data')
    ad = Ad(
        link=data.get('url', ''),
        description=data.get('descr', ''),
        created=data.get('date', None),
        contacts=contacts,
        flat=flat
    )
    ad.type = Ad.OWNER if data.get('type', 'owner') == 'owner' else Ad.RENTER
    ad.save()

    delta = now() - start_time
    logger.info('Succeed in {} seconds'.format(delta.seconds))
    return ad


# ------------------------------------------- WRAPPERS -------------------------------------------

# Обертка на парсеры
def wrap(func, name):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    def deco():
        # Заводим логгер
        logger = Logger()
        logger.name = 'Wrapper'
        logger.info('Parser "{}" task initializing...'.format(name))
        config = Parser.objects.get(name=name).get_config()
        logger.info('Got config: {}'.format(config))

        logger.info('Parsing...')
        logger.name = name
        start_time = now()
        raw_data = list(func(logger=logger, **config))  # Да да да, оптимищация будет потом
        logger.name = 'Wrapper'
        delta = now() - start_time
        logger.info('Parser succeed in {} seconds'.format(delta.seconds))

        logger.info('Creating objects...')
        logger.name = 'Create'
        start_time = now()
        objects = [create(i, logger) for i in raw_data]
        delta = now() - start_time
        logger.name = 'Wrapper'
        logger.info('{} objects created in {} seconds. Task done!'.format(len(objects), delta.seconds))

    deco.__name__ = 'parse_' + name

    return deco