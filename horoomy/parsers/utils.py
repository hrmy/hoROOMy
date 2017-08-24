from fuzzywuzzy.process import extractOne
from django.utils.timezone import make_aware, get_current_timezone
from horoomy.core.models import *
from traceback import format_exc
from horoomy.utils.logger import Logger
from horoomy.utils.data import *
from celery import shared_task
from horoomy.utils.dummy import Dummy

METROS = [i.name for i in Metro.objects.all()]
METROS_REPLACE = {
    'м.': '',
    'ул.': 'улица',
    'пр-т': 'проспект',
    'б-р': 'бульвар',
}


def get_metro(raw):
    raw = raw.lower().strip()
    for old, new in METROS_REPLACE.items():
        raw = raw.replace(old, new)
    best = extractOne(raw, METROS)[0]
    return Metro.objects.get(name=best)


def clean(data, **config):
    logger = config['logger']
    logger.info('Cleaning data...')
    data = dfilter(data)
    clean_data = {}

    # Metros
    logger.check_keys(data, 'metro')
    clean_data['metros'] = []
    raw_metros = data.get('metro', [])
    if isinstance(raw_metros, list) or isinstance(raw_metros, tuple):
        metros = []
        for raw in raw_metros:
            metro = trim(raw).lower()
            if metro.startswith('м.'):
                metro = metro.replace('м.', '').lstrip()
            if metro:
                metros.append(metro)
        clean_data['metros'] = metros

    # Flat location
    logger.check_keys(data, 'loc', 'adr')
    clean_data['address'] = trim(data.get('adr', ''))
    clean_data['lat'] = None
    clean_data['lon'] = None
    raw_loc = data.get('loc', None)
    if isinstance(raw_loc, str): raw_loc = trim(raw_loc).split(',')
    if isinstance(raw_loc, list) or isinstance(raw_loc, tuple):
        try:
            lat = cast(float, raw_loc[1])
            long = cast(float, raw_loc[0])
            if lat and long:
                clean_data['lat'] = lat
                clean_data['lon'] = long
        except:
            logger.warning('Invalid "loc" in "data": {}'.format(raw_loc))

    # Flat
    logger.check_keys(data, 'cost', 'area', 'room_num')
    clean_data['cost'] = cast(float, data.get('cost'))
    clean_data['area'] = cast(float, data.get('area'))
    clean_data['rooms'] = None
    raw_rooms = cast(int, data.get('room_num'))
    if raw_rooms == -1:
        clean_data['flat_type'] = Flat.TYPES.BED
    elif raw_rooms == 0:
        clean_data['flat_type'] = Flat.TYPES.ROOM
    else:
        clean_data['flat_type'] = Flat.TYPES.FLAT
        clean_data['rooms'] = raw_rooms

    # Contacts
    logger.check_keys(data, 'contacts')
    clean_data['contacts'] = dict.fromkeys(('name', 'phone', 'vk', 'fb'), '')
    raw_contacts = data.get('contacts', None)
    if raw_contacts:
        logger.check_keys(raw_contacts, 'person_name', 'phone')
        clean_data['contacts']['name'] = trim(raw_contacts.get('person_name', ''))
        clean_data['contacts']['phone'] = trim(raw_contacts.get('phone', ''))
        clean_data['contacts']['vk'] = trim(raw_contacts.get('vk', ''))
        clean_data['contacts']['fb'] = trim(raw_contacts.get('fb', ''))

    # Ad
    logger.check_keys(data, 'url', 'descr', 'date', 'type')
    clean_data['url'] = trim(data.get('url', ''))
    clean_data['description'] = trim(data.get('descr', ''))
    clean_data['parser'] = config['parser']
    clean_data['type'] = Ad.TYPES.OWNER if data.get('type', 'owner') == 'owner' else Ad.TYPES.RENTER
    clean_data['created'] = None
    raw_date = data.get('date')
    try:
        clean_data['created'] = make_aware(raw_date, get_current_timezone())
    except:
        logger.warning('Invalid "date" in "data": {}'.format(raw_date))

    # Images
    logger.check_keys(data, 'pics')
    clean_data['images'] = []
    raw_pics = data.get('pics')
    if isinstance(raw_pics, list) or isinstance(raw_pics, tuple):
        if all(map(lambda x: isinstance(x, str), raw_pics)):
            clean_data['images'].extend(map(trim, raw_pics))

    delta = logger.timestamp('started')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return clean_data


def create(data, **config):
    logger = config.get('logger', Dummy())
    logger.info('Creating objects...')

    # Metros
    metros = [Metro.objects.get_or_create(name=i)[0] for i in data['metros']]

    # Flat location
    flat_location = Location(
        address=data['address'],
        lat=data['lat'],
        lon=data['lon']
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
    images = [Image(type=Image.TYPES.REMOTE, ad=ad, url=i) for i in data['images']]
    Image.objects.bulk_create(images)

    delta = logger.timestamp('started')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return ad


# Обертка на парсеры
def wrap(func, name=None):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    @shared_task(name='parse.' + name.lower())
    def deco(**config):
        logger = Logger()
        logger.name = 'Wrapper'
        logger.status('Parser "{}" task initializing...'.format(name))

        parser = Parser.objects.get(name=name)
        config.update(parser.get_config())
        config['parser'] = parser
        logger.info('Got config: {}'.format(config))
        max_objects = config.get('max_objects', 100)
        max_errors = config.get('max_errors', 20)

        logger.status('Parsing...')
        logger.name = name.title()

        objects, errors, success = 0, 0, True
        try:
            for data in func(logger=logger.channel('Parser'), **config):
                try:
                    clean_data = clean(data, logger=logger.channel('Clean'), **config)
                    create(clean_data, logger=logger.channel('Create'), **config)
                except:
                    logger.error('Error during data processing:\n', format_exc())
                    errors += 1
                    if errors == max_errors:
                        logger.status('Max errors count reached: {}'.format(errors))
                        break
                else:
                    objects += 1
                    if objects == max_objects:
                        logger.status('Max objects count reached: {}'.format(objects))
                        break

                logger.info('Parsing...')
                logger.name = name.title()
        except:
            logger.status('Unexpected error - shutting down...')
            logger.error('Exception:\n', format_exc())
            errors += 1
            success = False

        logger.name = 'Wrapper'
        delta = logger.timestamp('started')
        logger.status('Parser task succeed in {} seconds'.format(delta.seconds))
        logger.status('Total objects created: {} / {}. Warm shutdown: {}'.format(objects, objects + errors, success))
        logger.report('{} Parser Task'.format(name.title()))

    return deco