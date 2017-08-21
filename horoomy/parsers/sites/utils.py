from django.utils.timezone import make_aware, get_current_timezone
from horoomy.core.models import *
from traceback import format_exc
from horoomy.utils.logger import Logger, TgBot
from horoomy.utils.data import *
from celery import shared_task


def clean(data, config):
    logger = config['logger']
    logger.name = 'Clean'
    logger.info('Cleaning data...')
    logger.timestamp('clean')
    clean_data = {}

    # Metros
    logger.check_keys(data, 'metro', name='data')
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
    logger.check_keys(data, 'loc', 'adr', name='data')
    clean_data['address'] = trim(data.get('adr', ''))
    clean_data['lat'] = None
    clean_data['lon'] = None
    raw_loc = data.get('loc', None)
    if isinstance(raw_loc, str): raw_loc = trim(raw_loc.split(','))
    if isinstance(raw_loc, list) or isinstance(raw_loc, tuple):
        try:
            lat = try_default(float, raw_loc[1])
            long = try_default(float, raw_loc[0])
            if lat and long:
                clean_data['lat'] = lat
                clean_data['lon'] = long
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
    logger.check_keys(data, 'url', 'descr', 'date', 'type', name='data')
    clean_data['url'] = trim(data.get('url'))
    clean_data['description'] = trim(data.get('descr'))
    clean_data['parser'] = config['parser']
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


def create(data, config):
    logger = config['logger']
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
    images = [Image(type=Image.REMOTE, ad=ad, url=i) for i in data['images']]
    Image.objects.bulk_create(images)

    delta = logger.timestamp('create')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return ad


# Обертка на парсеры
def wrap(func, name=None):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    @shared_task(name='parsers.' + name)
    def deco(**config):
        logger = Logger()
        logger.name = 'Wrapper'
        logger.info('Parser "{}" task initializing...'.format(name))
        
        parser = Parser.objects.get(name=name)
        config.update(parser.get_config())
        config['logger'] = logger
        config['parser'] = parser
        logger.info('Got config: {}'.format(config))
        max_objects = config.get('max_objects', 100)
        max_errors = config.get('max_errors', 20)

        logger.info('Parsing...')
        logger.name = name.title()

        objects, errors, success = 0, 0, True
        try:
            for data in func(**config):
                try:
                    clean_data = clean(data, config)
                    create(clean_data, config)
                except:
                    logger.error('Error during data processing:\n', format_exc())
                    errors += 1
                    if errors == max_errors:
                        logger.info('Max errors count reached: {}'.format(errors))
                        break
                else:
                    objects += 1
                    if objects == max_objects:
                        logger.info('Max objects count reached: {}'.format(objects))
                        break
                        
                logger.info('Parsing...')
                logger.name = name.title()
        except:
            logger.error('Unexpected error - shutting down...\n', format_exc())
            errors += 1
            success = False

        logger.name = 'Wrapper'
        delta = logger.timestamp('started')
        logger.info('Parser task succeed in {} seconds'.format(delta.seconds))
        logger.info('Total objects created: {} / {}. Warm shutdown: {}'.format(objects, objects + errors, success))
        TgBot.send(logger.get_text())

    return deco