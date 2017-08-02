import re
import json
import requests
import hashlib


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
