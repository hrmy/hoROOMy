from . import *


def parse(**kwargs):

    maxprice = kwargs.get('maxprice', 55000)
    logger = kwargs['logger']

    url = dict()

    p = Parse('bezPosrednikov')

    url['owners table'] = 'http://snimi-bez-posrednikov.ru/' \
                          'snyat-kvartiru?' \
                          'price=%s&' \
                          'tip[0]=квартира&' \
                          'komnat[0]=1&' \
                          'komnat[1]=2&' \
                          'komnat[2]=3&' \
                          'page=' % maxprice

    url['renters table'] = 'http://snimi-bez-posrednikov.ru/' \
                           'snimu-kvartiru?' \
                           'field_price_value=%s&' \
                           'field_tip_value[0]=квартира&' \
                           'komnat[0]=1&' \
                           'komnat[1]=2&' \
                           'komnat[2]=3&' \
                           'page=0' % maxprice

    url['room table'] = 'http://snimi-bez-posrednikov.ru/' \
                        'snyat-komnatu?' \
                        'price=%s&' \
                        'page=' % maxprice

    url['home'] = 'http://snimi-bez-posrednikov.ru'
    url['buy'] = '/snyat-kvartiru?'
    url['sell'] = '/snimu-kvartiru?'
    url['price'] = 'price='
    url['flat'] = 'tip[0]=квартира'
    url['rooms_amount'] = 'komnat[0]='
    url['metro'] = 'metro='
    url['page'] = 'page='

    url['daiy'] = 'snyat-posutochno'

    def parseOwner(advert_url):  # mode=0 - parse owner "sdam"; mode=1 - parse renter "snimu"

        # костыль для работы без декоратора, надо убрать
        try:

            print(url['home'] + advert_url)

            html = requests.get(url['home'] + advert_url).text
            soup = BeautifulSoup(html, 'html5lib')
            content = soup.find('div', {'class': 'node-content'})
            content = content.find('div', {'id': 'node-obyavlenie-full-group-content'})

            rooms_amount = content.find('section', {
                'class': 'field field-name-field-komnat field-type-list-text field-label-inline clearfix view-mode-full'})
            if not (rooms_amount is None):
                rooms_amount = rooms_amount.find('div', {'class': 'field-item even'})
                rooms_amount = int(rooms_amount.text)
            else:
                rooms_amount = 'NULL'

            photos_ = content.find('div', {
                'class': 'field field-name-field-foto field-type-image field-label-hidden view-mode-full'})
            photos = list()
            if not (photos_ is None):
                photos_ = photos_.find('div', {'class': 'field-items'})
                for a in photos_:
                    photos.append(a.a['href'])

            subway = content.find('section', {
                'class': 'field field-name-field-metro field-type-taxonomy-term-reference field-label-inline clearfix view-mode-full'})
            if not (subway is None):
                subway = subway.find('li', {'class': 'field-item even'})
                subway = [subway.text]
            else:
                subway = []

            to_subway = content.find('section', {
                'class': 'field field-name-field-min-do-metro field-type-number-integer field-label-inline clearfix view-mode-full'})
            if not (to_subway is None):
                to_subway = to_subway.find('div', {'class': 'field-item even'})
                to_subway = to_subway.text

            full_square = content.find('section', {
                'class': 'field field-name-field-ploshad field-type-number-decimal field-label-inline clearfix view-mode-full'})
            if not (full_square is None):
                full_square = full_square.find('div', {'class': 'field-item even'})
                full_square = full_square.text.split()
                full_square = int(full_square[0])
            else:
                full_square = 0

            price = content.find('section', {
                'class': 'field field-name-field-price field-type-number-integer field-label-inline clearfix view-mode-full'})
            if not (price is None):
                price = price.find('div', {'class': 'field-item even'})
                price = price.text.split()
                price = int(price[0]) * 1000  # + int(price[1])
            else:
                price = 0

            contacts = content.find('section', {
                'class': 'field field-name-field-tel field-type-text field-label-inline clearfix view-mode-full'})
            if not (contacts is None):
                contacts = contacts.find('div', {'class': 'field-item even'})
                contacts = contacts.text

            description = content.find('div', {
                'class': 'field field-name-body field-type-text-with-summary field-label-hidden view-mode-full'})
            if not (description is None):
                description = description.find('div', {'class': 'field-item even'})
                description = description.text

            adress = content.find('section', {
                'class': 'field field-name-field-adress field-type-text field-label-inline clearfix view-mode-full'})
            if not (adress is None):
                adress = adress.find('div', {'class': 'field-item even'})
                adress = adress.text

            features = content.find('section', {
                'class': 'field field-name-field-osobennosti field-type-list-text field-label-inline clearfix view-mode-full'})
            if not (features is None):
                features = features.find('div', {'class': 'field-item even'})
                features = features.text

            kitchen_square = content.find('section', {
                'class': 'field field-name-field-kuhnya field-type-number-decimal field-label-inline clearfix view-mode-full'})
            if not (kitchen_square is None):
                kitchen_square = kitchen_square.find('div', {'class': 'field-item even'})
                kitchen_square = kitchen_square.text.split()
                kitchen_square = int(kitchen_square[0])

            flat = dict()
            flat['room_num'] = rooms_amount
            flat['metro'] = subway
            flat['to_subway'] = to_subway
            flat['adr'] = adress
            flat['descr'] = description
            flat['features'] = features
            flat['area'] = full_square
            flat['kitchen_square'] = kitchen_square
            flat['cost'] = price
            flat['contacts'] = {'phone': contacts}
            flat['pics'] = photos
            flat['url'] = url['home'] + advert_url
            flat['loc'] = []

            return flat

        except:
            logger.error("BezPosrednikov: an error occured while parsing one flat")


    def parseOwnerList(b_url):
        try:
            html_pages = requests.get(b_url + '0').text
        except:
            logger.error('bezPosrednikov says: Whoops! Somethind went wrong. Error 1')
            return None

        soup_pages = BeautifulSoup(html_pages, 'html5lib')
        pages = soup_pages.find('li', {'class': 'pager-current odd'})
        pages = pages.text.split()
        pages = int(pages[2])

        for page in range(pages + 1):

            logger.info('bezPosrednikov is on page %d:' % page)
            p.write_status(page)

            try:
                full_url = '%s%d' % (b_url, page)
                print(full_url)
                html = requests.get(full_url).text
            except:
                logger.error('bezPosrednikov says: Whoops! Somethind went wrong. Error 2')
                return None

            soup = BeautifulSoup(html, 'html5lib')

            # ===========--------------
            pages2 = soup.find('li', {'class': 'pager-current odd'})
            pages2 = pages2.text.split()
            #logger.info("bezPosrednikov: pages")
            pages2 = int(pages2[0])
            # ===========---------------

            advert_table = soup.find('table', {'class': 'views-table cols-0'}).tbody

            if (advert_table is None):
                logger.error('bezPosrednikov says: Whoops! Somethind went wrong. Error 3')
                return None

            for tr in advert_table:
                advert_url = tr.a['href']

                if not (url['daiy'] in advert_url):
                    flat = parseOwner(advert_url)
                    try:
                        flat['date'] = tr.find('div', {'class': 'date'}).text
                        if b_url == url['owners table']:
                            p.append(flat)
                        else:
                            p.append_snimu(flat)
                    except:
                        logger.error('Error in bezPosrednikov -- writing to db!')
                        pass


    for b_url in [url['renters table'], url['owners table']]:  # url['room table']]:
        parseOwnerList(b_url)

    p.add_date()
    del p


