from celery import shared_task

@shared_task
def parse(maxprice=55000, **kwargs):

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
        # try:
        cost = soup.find('section', class_='clear-fix').find('div', class_='object-block').find('div',
                                                                                                class_="object-info-block").find(
            'div', class_='object-price').text.split('/')[0][:-2]
        cost = cost.split()
        cost = int(''.join(cost))
        # except:
        # cost = '-'

        # metro
        try:
            metro = []
            metro.append(info.find('div', class_='object-info-link_l1').find('a').text)
        except:
            metro = []

            # Address
            # try:
            # adr = ''
            # elms = info.find('div', class_='object-info-link_l2')#.find_all('a')
            # # for elm in elms:
            # #     print(elm)
            # #     adr += elm.text + ' '
            # print(elms)
            # except:
            #   adr = '-'

        # Created date
        date = media.find('div', class_='obj-info-dop').text.split()[1][:-1]
        date = date.split('.')
        date[2] = '20' + str(date[2])
        date = '.'.join(date)
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

        # loc
        # loc = []
        # if not adr:
        #   headers = {
        #       'Referer': 'http://www.realestate.ru/flatrent/4320916/',
        #       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        #   }

        #   response = requests.get('http://www.realestate.ru/scripts/common/ymaps.js', headers=headers).text
        #   start = response.find("center:") + 9
        #   ch = ''
        #   i = 0
        #   while ch != ']':
        #       ch = response[start+i]
        #       i += 1
        #   end = start + i -1
        #   loc = response[start:end].split(',')


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


    maxprice = int(maxprice)
    #p = Parse('realEstate')
    currentPage = 1

    template = 'http://www.realestate.ru'
    # http://www.realestate.ru/flatrent/s/rcs10.1.2.3-rgs1.2.3.4.5.6.7.8.9.10-prt30/
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
            url = template + ad.find('div', class_='obj-item').find('a').get('href')
            # lat = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lat') # Получаем широту и долготу
            # lng = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lng') # скрытые в названии объявления
            adr = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').text

            html = get_html(url)
            print(url)
            date, cost, descr, pics, room_num, area, metro, contacts = get_page_data(html)

            data = {'date': date, 'cost': cost, 'descr': descr, 'pics': pics, 'room_num': room_num, 'area': area,
                    'adr': adr, 'metro': metro, 'url': url, 'contacts': contacts}
            yield data

            #p.write_status(currentPage)

    #p.add_date()
    # todo: signal that parsing is over
