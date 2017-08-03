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

def create(data):

    # contacts
    contacts_dic = data['contacts']
    contacts = Contacts(
        phone = contacts_dic['phone'],
        vk = contacts_dic.get('vk', ""),
        fb = contacts_dic.get('fb', "")
    )

    # metros
    metros = data['metro']

    #todo: тут надо прописать добавление станций метро


    # Ad
    ad = Ad(link = data['url'],
            description = data['descr'],
            contacts = contacts,
            created = data['date']
            )

    # flat cost
    flat = Flat(cost = data['cost'])

    if 'loc' in data:   # объявление "сдам"
        ad.type = '0'
        # flat area
        flat.area = data['area']

        # flat type & rooms
        if data['room_num'] == 0:
            flat.type = '1'
        elif data['room_num'] == -1:
            flat.type = '2'
        else:
            flat.type='0'
            flat.rooms = data['room_num']

        # flat location
        if data['loc'] != 'YANDEXLOCERR':
            location = Location(address = data['adr'],
                                lat = data['loc'][1],
                                long = data['loc'][0]
                                )
            flat.location = location

    else:   # объявление "сниму"
        ad.type = '1'

        # flat cost
        cost = data.get('cost', None)
        if cost is not None:
            flat.cost = cost

    # flat
    ad.flat = flat

    return {Flat: flat, Location: location, Ad: ad}


# ------------------------------------------- WRAPPERS -------------------------------------------

# Обертка на парсеры
def wrap(func, name):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    def deco():
        # Получаем конфиг для парсера
        config = Parser.objects.get(name=name).get_config()
        # Запускаем саму функцию, она должна вернуть итератор по словарям
        raw_data = func(**config)
        # Создаем объекты БД из полученных словарей (пока не пушим)
        objects = [Flat(**i) for i in raw_data]
        # Разом запихиваем все объекты в БД (спасибо bulk_create)
        Flat.objects.bulk_create(objects)

    deco.__name__ = 'parse_' + name

    return deco
