from requests import get


class YMapsAPI:
    GEOCODE_URL = 'https://geocode-maps.yandex.ru/1.x/'

    @staticmethod
    def get_geodata(location):
        address = location.address
        lat, lon = location.lat, location.lon
        if not address and not (lat and lon):
            raise ValueError('Location object don\'t have any geodata')
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
        address = data['Address']['formatted']
        exact = data['precision'] == 'exact'
        return {'lat': lat, 'lon': lon, 'address': address, 'exact': exact}