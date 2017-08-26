from fuzzywuzzy.process import extractOne, extractBests
from fuzzywuzzy.fuzz import token_sort_ratio
from django.utils.timezone import make_aware, get_current_timezone
from django.core.exceptions import ValidationError
from horoomy.core.models import *
from traceback import format_exc
from horoomy.utils.logger import Logger
from horoomy.utils.models import table_exists
from horoomy.utils.data import *
from celery import shared_task

METROS = [i.name for i in Metro.objects.all()] if table_exists('core_metro') else []
METROS_THRESHOLD = 30
METROS_REPLACE = {
    'м.': '',
    'ул.': 'улица',
    'пр-т': 'проспект',
    'б-р': 'бульвар',
}
DESCRIPTION_THRESHOLD = 80


def get_metro(raw):
    raw = raw.lower().strip()
    for old, new in METROS_REPLACE.items():
        raw = raw.replace(old, new)
    best, ratio = extractOne(raw, METROS)
    if ratio < METROS_THRESHOLD: return None
    return Metro.objects.get(name=best)


def get_duplicates(data):
    ad = data['ad']
    ads = Ad.objects.all()
    if ad.pk: ads = ads.exclude(pk=ad.pk)
    duplicates = extractBests(
        ad, ads,
        processor=lambda x: x.description,
        scorer=lambda *x: token_sort_ratio(*x, force_ascii=False),
        score_cutoff=DESCRIPTION_THRESHOLD,
        limit=None
    )
    return duplicates


def fix_phone(raw):
    digits = re.sub(r'[^\d]+', '', raw)
    if len(digits) < 10: return None
    digits = digits[-10:]
    phone = '8 ({}) {}-{}-{}'.format(digits[0:3], digits[3:6], digits[6:8], digits[8:10])
    return phone


# Пытается подогнать сырые данные парсеров к нормальным названиям ключей и типам данных
def fix(data, **config):
    logger = config['logger'].channel('Fix')
    logger.info('Cleaning data...')
    data = dfilter(data)
    clean_data = {}

    # Metros
    logger.check_keys(data, 'metro')
    raw_metros = data.get('metro')
    if isinstance(raw_metros, list) or isinstance(raw_metros, tuple):
        clean_data['metros'] = []
        for raw in raw_metros:
            metro = cast(trim, raw)
            if not metro: continue
            clean_data['metros'].append(metro)

    # Flat location
    logger.check_keys(data, 'loc', 'adr')
    clean_data['address'] = cast(trim, data.get('adr'))
    raw_loc = data.get('loc')
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
    raw_rooms = cast(int, data.get('room_num'))
    if isinstance(raw_rooms, int):
        if raw_rooms == -1:
            clean_data['flat_type'] = Flat.TYPES.BED
        elif raw_rooms == 0:
            clean_data['flat_type'] = Flat.TYPES.ROOM
        else:
            clean_data['flat_type'] = Flat.TYPES.FLAT
            clean_data['rooms'] = raw_rooms

    # Contacts
    logger.check_keys(data, 'contacts')
    clean_data['contacts'] = {}
    raw_contacts = data.get('contacts')
    if isinstance(raw_contacts, dict):
        logger.check_keys(raw_contacts, 'person_name', 'phone')
        clean_data['contacts']['name'] = cast(trim, raw_contacts.get('person_name'))
        clean_data['contacts']['phone'] = cast(fix_phone, raw_contacts.get('phone'))
        clean_data['contacts']['vk'] = cast(trim, raw_contacts.get('vk'))
        clean_data['contacts']['fb'] = cast(trim, raw_contacts.get('fb'))

    # Ad
    logger.check_keys(data, 'url', 'descr', 'date', 'type')
    clean_data['url'] = cast(trim, data.get('url'))
    clean_data['description'] = cast(trim, data.get('descr'))
    clean_data['type'] = Ad.TYPES.OWNER if data.get('type', 'owner') == 'owner' else Ad.TYPES.RENTER
    raw_date = data.get('date')
    try:
        clean_data['created'] = make_aware(raw_date, get_current_timezone())
    except:
        logger.warning('Invalid "date" in "data": {}'.format(raw_date))

    # Images
    logger.check_keys(data, 'pics')
    raw_pics = data.get('pics')
    if isinstance(raw_pics, list) or isinstance(raw_pics, tuple):
        clean_data['images'] = []
        for raw in raw_pics:
            image = cast(trim, raw)
            if not image: continue
            clean_data['images'].append(raw)

    clean_data = dfilter(clean_data)
    delta = logger.timestamp('started')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return clean_data


def evolve(data, **config):
    logger = config['logger'].channel('Evolve')
    logger.info('Evolving data...')
    clean_data = {}

    # Metros
    clean_data['metros'] = []
    for raw in data.get('metros', []):
        metro = get_metro(raw)
        if metro is None: continue
        clean_data['metros'].append(metro)

    # Flat location
    flat_location = Location(
        address=data.get('address', ''),
        lat=data.get('lat'),
        lon=data.get('lon')
    )
    flat_location.exact = flat_location.evolve()
    clean_data['flat_location'] = flat_location

    # Flat
    clean_data['flat'] = Flat(
        type=data.get('flat_type', Flat.TYPES.FLAT),
        cost=data.get('cost'),
        area=data.get('area'),
        rooms=data.get('rooms'),
    )

    # Contacts
    raw_contacts = data.get('contacts', {})
    clean_data['contacts'] = Contacts(
        name=raw_contacts.get('name', ''),
        phone=raw_contacts.get('phone', ''),
        vk=raw_contacts.get('vk', ''),
        fb=raw_contacts.get('fb', '')
    )

    # Ad
    clean_data['ad'] = Ad(
        type=data.get('type', Ad.TYPES.OWNER),
        url=data.get('url', ''),
        description=data.get('description', ''),
        created=data.get('created'),
    )
    try:
        clean_data['ad'].clean_fields(('flat', 'contacts'))
    except ValidationError:
        clean_data['ad'].url = ''

    # Images
    clean_data['images'] = []
    for raw in data.get('images', []):
        image = Image(type=Image.TYPES.REMOTE, url=raw)
        try:
            image.clean_fields(('ad',))
        except ValidationError:
            continue
        clean_data['images'].append(image)

    delta = logger.timestamp('started')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return clean_data


def validate(data, **config):
    logger = config['logger'].channel('Validate')
    logger.info('Validating objects...')

    # Mandatory
    logger.info('Checking mandatory data...')
    logger.info('Phone provided:', bool(data['contacts'].phone))
    logger.info('Flat location:', data['flat_location'])
    logger.info('Location precision:', data['flat_location'].exact)
    logger.info('Ad url provided:', bool(data['ad'].url))
    duplicates = get_duplicates(data)
    logger.info('Ad duplicates:', duplicates)
    valid = not any((
        not data['contacts'].phone,
        data['flat_location'].exact is None,
        not data['ad'].url,
        duplicates,
    ))
    if not valid: return False

    # Complete
    logger.info('Checking other data...')
    logger.info('Ad type:', Ad.TYPES[data['ad'].type])
    logger.info('Flat type:', Flat.TYPES[data['flat'].type])
    logger.info('Flat cost provided:', bool(data['flat'].cost))
    logger.info('Flat area provided:', bool(data['flat'].area))
    logger.info('Flat rooms provided:', bool(data['flat'].rooms))
    complete = False
    if data['ad'].type == Ad.TYPES.OWNER:
        complete = not any((
            not data['flat_location'].exact,
            not data['flat'].cost,
            not data['flat'].area,
            data['flat'].type == Flat.TYPES.FLAT and not data['flat'].rooms,
        ))
    logger.info('Complete:', complete)
    data['ad'].complete = complete

    delta = logger.timestamp('started')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return data


def create(data, **config):
    logger = config['logger'].channel('Create')
    logger.info('Creating objects...')

    data['flat_location'].save()
    data['flat'].location = data['flat_location']
    data['flat'].save()
    data['flat'].metros.add(*data['metros'])
    data['contacts'].save()
    data['ad'].contacts = data['contacts']
    data['ad'].flat = data['flat']
    data['ad'].parser = config.get('parser')
    data['ad'].save()
    for i in data['images']: i.ad = data['ad']
    Image.objects.bulk_create(data['images'])

    delta = logger.timestamp('started')
    logger.info('Succeed in {:.3f} seconds'.format(delta.total_seconds()))
    return data['ad']


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
        # TODO: FIX (IN PARSERS)
        config['logger'] = logger.channel('Parser')
        logger.info('Got config:', config)
        max_objects = config.get('max_objects', 100)
        max_errors = config.get('max_errors', 20)

        logger.status('Parsing...')
        logger.name = name.title()

        # TODO: FIX
        objects, errors, success = 0, 0, True
        complete_objects, raw_objects, invalid_objects = 0, 0, 0
        try:
            for data in func(**config):
                try:
                    data = fix(data, **config)
                    data = evolve(data, **config)
                    data = validate(data, **config)
                    if not data:
                        logger.warning('Validation failed')
                        invalid_objects += 1
                    else:
                        if data['ad'].complete:
                            complete_objects += 1
                        else:
                            raw_objects += 1
                        create(data, **config)
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
        except:
            logger.status('Unexpected error - shutting down...')
            logger.error('Exception:\n', format_exc())
            errors += 1
            success = False

        delta = logger.timestamp('started')
        logger.status('Parser task succeed in {} seconds'.format(delta.seconds))
        logger.status('Total objects created: {} / {}. Warm shutdown: {}'.format(
            objects,
            objects + errors,
            success
        ))
        logger.status('Complete objects: {}. Raw objects: {}. Invalid objects: {}'.format(
            complete_objects,
            raw_objects,
            invalid_objects
        ))
        logger.report('{} Parser Task'.format(name.title()))

    return deco