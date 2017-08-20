from requests import get


class YMapsAPI:
    GEOCODE_URL = 'https://geocode-maps.yandex.ru/1.x/'

    @staticmethod
    def get_geodata(location):
        address = location.address
        lat, lon = location.lat, location.lon
        data = {
            'kind': 'house',
            'lang': 'ru_RU',
            'results': 1,
            'format': 'json',
            'geocode': address if address else '{},{}'.format(lon, lat)
        }
        json = get(YMapsAPI.GEOCODE_URL, params=data).json()
        data = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        lon, lat = map(float, data['Point']['pos'].split(' '))
        data = data['metaDataProperty']['GeocoderMetaData']
        address = None
        if data['precision'] == 'exact':
            address = data['Address']['formatted']
        return {'lat': lat, 'lon': lon, 'address': address}