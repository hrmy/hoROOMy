from . import *
from celery import shared_task

@shared_task
@json_check
def parse(**kwargs):

    def get_html(url):
        r = requests.get(url)
        print(str(r), end=' ')
        return r.text

    def get_page_data(html):

        soup = BeautifulSoup(html, 'lxml')

        media = soup.find('section', class_='clear-fix').find('div', class_='object-block').find('div',
                                                                                                 class_="object-info-block").find(
            'div', class_='object-media')
        info = soup.find('section', class_='clear-fix').find('div', class_='object-block').find('div',
                                                                                                class_="object-info-block").find(
            'div', class_='object-info')

        # price
        cost = soup.find('section', class_='clear-fix').find('div', class_='object-block').find('div',
                                                                                                class_="object-info-block").find(
            'div', class_='object-price').text.split('/')[0][:-2]
        cost = cost.split()
        cost = int(''.join(cost))


        # metro
        try:
            metro = []
            metro.append(info.find('div', class_='object-info-link_l1').find('a').text)
        except:
            metro = []

        # Created date
        date = media.find('div', class_='obj-info-dop').text.split()[1][:-1]
        date = date.split('.')
        date[2] = '20' + str(date[2])
        date = '.'.join(date)
        date = datetime.strptime(date, '%d.%m.%Y')
        # date = '-'



        temp = info.find('div', class_='object-params').find('div', class_='params-block').find_all('div',
                                                                                                    class_='params-item')
        for i in range(len(temp)):
            t = temp[i].find('div', class_='float-left').text
            if 'Количество комнат' in t:
                room_num_i = i
            elif 'Общая площадь' in t:
                area_i = i


                # Rooms
        room_num = info.find('div', class_='object-params').find('div', class_='params-block').find_all('div', class_='params-item')[room_num_i].find('div', class_='float-right').text
        if room_num == 'комната':
            room_num = 0
        else:
            room_num = int(room_num)



            # Area
        area = int(info.find('div', class_='object-params').find('div', class_='params-block').find_all('div',
                                                                                                        class_='params-item')[
                       area_i].find('div', class_='float-right').text.split()[0])

        # Description

        descr = info.find('div', class_='object-description').find('div', class_='object-description-text').text

        pics = []
        template = 'http://www.realestate.ru'
        elms = media.find('div', class_='object-photo').find('div', class_='other-photo-container').find_all('img',
                                                                                                             class_='other-photo')
        if elms:
            for elm in elms:
                pics.append(template + elm.get('src'))

        # Contacts

        contacts = {'vk': "", 'fb': "", 'email': "", 'phone': ""}
        add = int(media.find('div', class_='obj-active-panel').find('div', class_='toogle-button').get('blst'))
        if add == 0:
            add = int(media.find('div', class_='obj-active-panel').find('div', class_='toogle-button').get('lst1'))
        add = str(add // 17)[1:]
        phone = media.find('div', class_='object-connect').find('div', class_='object-builder-phone_block').find('div',
                                                                                                                 class_='object-builder-phone').text[
                :-3] + add
        # print(phone)
        contacts['phone'] = phone


        # print(date, cost, room_num, area, contacts, sep = '\n')
        return date, cost, descr, pics, room_num, area, metro, contacts

        # Location // Можно вытащить из названия объявления

    def get_total_pages(url):
        soup = BeautifulSoup(get_html(url), 'lxml')
        total_pages = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div',
                                                                                                              class_='main-content').find(
            'div', class_='list-panel').find('div', class_='more-info').find_all('a')[-1].get('href').split('pg')[1][
                      :-1]
        return int(total_pages)


    maxprice = int(kwargs.get('maxprice', 55000))
    currentPage = 1

    template = 'http://www.realestate.ru'
    page_url_template = 'http://www.realestate.ru/flatrent/s/rcs10.1.2.3--rgs1.2.3.4.5.6.7.8.9.10-prt{0}/pg'.format(maxprice // 1000)  # 'http://www.realestate.ru/flatrent/pg'
    page_url = page_url_template + str(currentPage) + '/'
    total_pages = get_total_pages(page_url) + 1

    for currentPage in range(total_pages):
        # if currentPage == 2:
        #   break
        page_url = page_url_template + str(currentPage) + '/'
        soup = BeautifulSoup(get_html(page_url), 'lxml')
        ads = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div',
                                                                                                      class_='main-content').find(
            'div', class_='list-panel').find_all('div', class_='obj')

        for ad in ads:
            try:
                url = template + ad.find('div', class_='obj-item').find('a').get('href')
                adr = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').text

                html = get_html(url)
                print(url)
                date, cost, descr, pics, room_num, area, metro, contacts = get_page_data(html)

                data = {'type': "owner", 'date': date, 'cost': cost, 'descr': descr, 'pics': pics, 'room_num': room_num, 'area': area,
                        'adr': adr, 'metro': metro, 'url': url, 'contacts': contacts, 'loc': None}
                yield data
            except:
                alertExc()

    # todo: signal that parsing is over
