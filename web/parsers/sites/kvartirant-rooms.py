from . import *


def get_html(url):
    r = requests.get(url)
    return r.text


def get_page_data(html, url):
    print(url)

    soup = BeautifulSoup(html, 'lxml')
    base = soup.find('div', class_='boxed-container').find_all('div', class_='bg_lightgray')[0].find('div',
                                                                                                     class_='container').find(
        'div', class_='col-md-8 col-obj').find('div', class_='row')

    # f
    area = ''
    metro = ''
    adr = ''

    temp = base.find('div', class_='col-xs-12 obj-info').find_all('span')
    for i in range(len(temp)):
        if 'Площадь' in temp[i].text:
            try:
                area = float(temp[i].text.split()[1])
            except:
                area = '-'
        elif 'Метро' in temp[i].text:
            metro = temp[i].text.split('\u2022')
            metro[0] = ' '.join(metro[0].split()[1:])
        elif 'Адрес' in temp[i].text:
            adr = temp[i].text.split()[1:]
            adr = ' '.join(adr)

    # Определяем, посуточная аренда или нет
    try:
        isDaily = base.find('div', class_='col-xs-12 obj-info').find_all('span', class_='red')[1].text
        if isDaily == 'ПОСУТОЧНАЯ АРЕНДА':
            return False
    except:
        pass


    # Room number
    room_num = 0

    # Cost
    cost = base.find('div', class_='col-xs-12 obj-info').find('h3').find('span', class_='text-nowrap red').text
    cost = cost.split()[1:]
    cost = int(''.join(cost))

    # Date
    date = \
        base.find('div', class_='col-xs-12 col-sm-4 text-center padding_t10 obj-data').text.split()[0].split(':')[1]
    if (date == 'Сегодня'):
        date = str(datetime.today()).split()[0].split('-')
        date = '.'.join(list(reversed(date)))
    else:
        date = date.replace('/', '.')
    date = datetime.strptime(date, '%d.%m.%Y')

    # Contacts
    contacts = {'vk': "", 'fb': "", 'email': "", 'phone': ""}
    phone = base.find('div', class_='col-xs-12 col-sm-8 padding_t10 obj-contact').find('span', class_='red').find(
        'b').text.split("write('")[-1][:-2]  # Вот такой-вот костыль
    contacts["phone"] = phone

    # Descr
    descr = base.find('div', class_='col-xs-12 obj-info').find('p').text

    # Pics
    pics = []
    temp = base.find('div', class_='text-center col-xs-12 obj-info').find('div', class_='bxContainer').find(
        'ul').find_all('li')
    for li in temp:
        pics.append('http://www.kvartirant.ru' + li.find('a').get('href'))

    # loc
    loc = []
    if not adr or adr == '-':
        temp = str(soup.find_all('script', type='text/javascript')[-1])
        sr = temp.find("ymaps.geocode('")
        start = sr + 15
        i = 0
        ch = ''
        while ch != "'":
            ch = temp[start + i]
            i += 1
        loc = temp[start:start + i - 1].split()

    from math import trunc
    try:
        area = trunc(float(area))
    except:
        area = 0

    data = {"type": "owner", "cost": cost, "date": date, "contacts": contacts, "pics": pics, "descr": descr, "adr": adr, "loc": loc,
            "metro": metro, "area": area, "room_num": room_num, "url": url}
    return data


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    total_pages = soup.find('div', class_='boxed-container').find('div', class_='base-pagination').find('ul',
                                                                                                        class_='pagination').find(
        'li', class_='last').find('a').get('data-page')

    return int(total_pages) + 1


def get_objects_group(html):
    soup = BeautifulSoup(html, 'lxml')
    groups = soup.find('div', class_='boxed-container').find_all('div', class_='bg_lightgray')[0].find('div',
                                                                                                       class_='container').find_all(
        'div', class_='col-md-8 col-obj')
    return groups


def parse(**kwargs):
    maxprice = kwargs.get('maxprice', 55000)
    logger = kwargs['logger']

    base_url = 'http://www.kvartirant.ru/bez_posrednikov/Moskva/sniat-komnatu/'
    params = '&cost_limit={0}'.format(maxprice)
    template = 'http://www.kvartirant.ru'
    html = get_html(base_url)
    total_pages = get_total_pages(html)
    for page in range(total_pages)[1:]:
        url = base_url + '?page=' + str(page) + params
        html = get_html(url)
        groups = get_objects_group(html)
        for group in groups:
            ads = group.find('div', class_='row').find_all('div', class_='obj-contact')
            for ad in ads:
                url = ad.find('span', class_='red').find('b').find('a').get('href')
                temp_html = get_html(template + url)
                print('Page ' + str(page), end=' - ')
                page_data = get_page_data(temp_html, template + url)
                if page_data:
                    yield page_data
                    logger.info('Kvartirant-rooms: one more owner')
                else:
                    logger.info('Kvartirant-rooms: Daily')  # | room_num more than 3 rooms | cost more than maxprice')

    logger.info('Done!')