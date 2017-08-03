import re
import sys
import hashlib
from . import *
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
        loc = loc[1] + "," + loc[0]
        print("!!!GET_LOC USED!!!")
        return loc

    # get address if we know coordinates
    def get_adr(loc):
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
    if (data['loc'] == []) or (data['loc'] == "") or (data['loc'] is None):
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


# check the json each parser returns, add some info or detect errors
# see evolve() definition for more info
def json_check(function):
    def wrap(**kwargs):
        data = evolve(function(**kwargs))
        yield data
    return wrap

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