# This Python file uses the following encoding: utf-8

import re
import json
import time
import base64
import datetime
import requests
import threading
from bs4 import BeautifulSoup
from time import gmtime, strftime
from datetime import datetime, timedelta
from parser_class import Parse
from datetime import date as datetimedate
from driveAPI import BackuppedFile, upload_db
from botAPI import alertExc, tgExcCatch, alertBot, tgExcnoargs

#===================================SDAM BEZ POSREDNIKOV=============================




#============================================CIAN==CIAN====================================


import requests
import json
from bs4 import BeautifulSoup




#=========================================POSREDNIKOVZDES-NET=======================================

#---------------------------------------------SDAM-----------------------------------------

@tgExcnoargs    
def posrednikovnetSdam():

    def delliter(stri):
        while True:
            l = stri.find('<')
            g = stri.find('>')
            delit = stri[l:g + 1]
            if delit == '<br/>':
                stri = stri.replace(delit, '\n')
            else:
                stri = stri.replace(delit, '')

            if l == -1:
                break
        return stri

    p = Parse('posrednikovNet')
    counter = 0
    u = 'http://msk.posrednikovzdes.net/adv.php?city=73&oper=3'
    text = requests.get(u).text
    pages = str(text)[str(text).find('Страницы'):]
    pages = pages[:pages.find('<TBODY>')]
    s = BeautifulSoup(pages, 'lxml')
    a = str(s.find_all('a')[-1].get('href'))
    a = int(a[a.find('page=') + 5:a.rfind('&')])
    ALL_OFFERS = []
    for al in range(1, a + 1):
        #print(al)
        u = 'http://msk.posrednikovzdes.net/adv.php?city=73&oper=3&metro=0&realty=0&oplt=0&price1=0&price2=11&page=%s&paiin=0' % al
        text = requests.get(u).text
        soup = BeautifulSoup(text, "lxml")
        table = soup.find('table', {'class': 'tab'})
        tr = table.find_all('tr')  # [/// , /// , ///]
        for i in tr:
            td = i.find_all('td')
            if len(td) == 9:
                dat = delliter(str(td[1]))
                idd = dat[dat.find('№') + 1:]
                idd = re.sub(r" |\n", '', idd)
                # print(idd)
                url = 'http://msk.posrednikovzdes.net/offer.php?id=%s' % idd
                # print(url)

                dat = dat[:dat.find('№')]
                dat = re.sub(r'\d\d:\d\d:\d\d', '', dat)
                if "Сегодня" in dat:
                    dat = datetimedate.today().strftime("%d.%m.%Y")
                elif "Вчера" in dat:
                    yesterday = datetimedate.today() - timedelta(1)
                    dat = yesterday.strftime("%d.%m.%Y")
                # print(dat)

                obj = delliter(str(td[2]))
                obj = obj.split('\n')
                distr = None
                street = None
                metro = None
                for j in range(len(obj)):
                    obj[j] = re.sub(r'\xa0|\t|\r', '', obj[j])
                    if 'Район' in obj[j]:
                        distr = obj[j]
                    if "Улица" in obj[j]:
                        street = obj[j]
                    if 'Метро' in obj[j]:
                        metro = obj[j]
                room = obj[1]
                if "квартира" in room:
                    room = int(re.sub(r'квартира|к\.|-| ', '', room))
                elif "Койко-место" in room:
                    room = -1
                elif "Комната" in room:
                    room = 0
                # print(room, distr, street, metro, sep='||')

                pay = delliter(str(td[3]))
                pay = re.sub(r'\xa0|\t|\r', '', pay).split('\n')
                if len(pay) < 3:
                    payment = "no"
                else:
                    payment = pay[0] + pay[1] + pay[2]
                payment = re.sub(r'Помесячно| |Предоплата|Посуточно|Залог', '', payment)
                if 'тыс.руб.' in payment:
                    payment = re.sub(r'тыс\.руб\.', '', payment)
                    if '.' in payment:
                        payment = payment.replace('.', '')
                        payment += '00'
                    else:
                        payment += '000'
                elif 'руб.' in payment:
                    payment = re.sub(r'руб\.', '', payment)
                # print(payment)

                floor = delliter(str(td[4]))
                # print(floor)

                area = delliter(str(td[5]))
                if "Общ" in area:
                    area = area.split('\n')
                    area = float(re.sub(r'м2| ', '', area[1]))
                elif len(area) == 0:
                    area = 0
                else:
                    area = area.split('\n')
                    area = float(re.sub(r'м2| ', '', area[1]))
                # print(area)

                descript = td[7].find('span', {'style': "color:#CC0000; "}).text
                # print(descript)

                phone = delliter(str(td[7]))
                phone = re.sub(r'\xa0|\t|\r', '', phone).split('\n')
                for z in phone:
                    if "Контакты" in z:
                        ph = z[z.find('+'):]
                        ph = ph[:17]
                # print(ph)

                photo = str(td[7])
                allPhoto = []
                if 'Фото' in photo:
                    photo = photo[photo.find('javascript:showfoto'):]
                    photo = photo[photo.find('(') + 1:photo.find(')')]
                    photo = re.sub(r'\'|jpeg|z|\.|,', '', photo)
                    photo = re.sub(idd, '', photo)
                    photo = int(photo[-1])
                    for a in range(1, photo + 1):
                        uu = 'http://www.posrednikovzdes.net/foto/files2/%s_b_%s.jpeg' % (idd, a)
                        allPhoto.append(uu)
                # print(allPhoto)
                x = {'room_num': room, 'metro': metro, 'pics': allPhoto,
                     "cost": payment, "floor": floor, "contacts": dict(phone=ph, person_name=None), "loc": "",
                     "url": url, "date": dat, "area": area, "adr": str(distr) + " " + str(street), "descr": descript}
                try:
                    p.append(x)
                except:
                    alertExc()
                
                counter += 1
                p.write_status(counter)
                # print('[+]')
        time.sleep(1)
    p.add_date()
    del p

#---------------------------------------------SNIMU------------------------------------------------

@tgExcnoargs
def posrednikovnetSnimu():

    def delliter(stri):
        while True:
            l = stri.find('<')
            g = stri.find('>')
            delit = stri[l:g + 1]
            if delit == '<br/>':
                stri = stri.replace(delit, '\n')
            else:
                stri = stri.replace(delit, '')

            if l == -1:
                break
        return stri


    p = Parse('posrednikovNet')
    counter = 0
    u = 'http://msk.posrednikovzdes.net/adv.php?city=73&oper=4'
    text = requests.get(u).text
    pages = str(text)[str(text).find('Страницы'):]
    pages = pages[:pages.find('<TBODY>')]
    s = BeautifulSoup(pages, 'lxml')
    a = str(s.find_all('a')[-1].get('href'))
    a = int(a[a.find('page=') + 5:a.rfind('&')])
    ALL_OFFERS = []
    for al in range(1, a + 1):
        #print(al)
        u = 'http://msk.posrednikovzdes.net/adv.php?city=73&oper=4&metro=0&realty=0&oplt=0&price1=0&price2=0&page=%s&paiin=0' % al
        text = requests.get(u).text
        soup = BeautifulSoup(text, "lxml")
        table = soup.find('table', {'class': 'tab'})
        tr = table.find_all('tr')  # [/// , /// , ///]
        for i in tr:
            td = i.find_all('td')
            if len(td) == 9:
                dat = delliter(str(td[1]))
                idd = dat[dat.find('№') + 1:]
                idd = re.sub(r' ', '', idd)
                # print(idd)
                url = 'http://msk.posrednikovzdes.net/offer.php?id=%s' % idd
                # print(url)

                dat = dat[:dat.find('№')]
                dat = re.sub(r'\d\d:\d\d:\d\d', '', dat)
                if "Сегодня" in dat:
                    dat = datetimedate.today().strftime("%d.%m.%Y")
                elif "Вчера" in dat:
                    yesterday = datetimedate.today() - timedelta(1)
                    dat = yesterday.strftime("%d.%m.%Y")
                # print(dat)

                obj = delliter(str(td[2]))
                obj = obj.split('\n')
                distr = None
                metro = None
                for j in range(len(obj)):
                    obj[j] = re.sub(r'\xa0|\t|\r', '', obj[j])
                    if 'Район' in obj[j]:
                        distr = obj[j]
                    if 'Метро' in obj[j]:
                        metro = obj[j]
                room = obj[1]
                if "квартира" in room:
                    room = int(re.sub(r'квартира|к\.|-| ', '', room))
                elif "Койко-место" in room:
                    room = -1
                elif "Комната" in room:
                    room = 0
                # print(room, distr, metro, sep='||')

                pay = delliter(str(td[3]))
                pay = re.sub(r'\xa0|\t|\r', '', pay).split('\n')
                if len(pay) < 3:
                    payment = 0
                else:
                    payment = pay[0] + pay[1] + pay[2]
                #print(payment)
                if str(payment) != '0':
                    payment = re.sub(r'Помесячно| |Предоплата|Посуточно', '', payment)
                else:
                    payment = '0'
                    
                if 'тыс.руб.' in payment:
                    payment = re.sub(r'тыс\.руб\.', '', payment)
                    if '.' in payment:
                        payment = payment.replace('.', '')
                        payment += '00'
                    else:
                        payment += '000'
                elif 'руб.' in payment:
                    payment = re.sub(r'руб\.', '', payment)
                # print(payment)

                descript = td[7].find('span', {'style': "color:#CC0000; "}).text
                # print(descript)

                phone = delliter(str(td[7]))
                phone = re.sub(r'\xa0|\t|\r', '', phone).split('\n')
                for z in phone:
                    if "Контакты" in z:
                        ph = z[z.find('+'):]
                        ph = ph[:17]
                # print(ph)

                x = {'room_num': room, 'metro': metro,
                     "cost": payment,  "contacts": dict(phone=ph, person_name=None), "loc": "",
                     "url": url,  "date": dat, "adr": str(distr), "descr": descript, "pics": None}
                try:
                    p.append_snimu(x)
                except:
                    alertExc()
                counter += 1
                p.write_status(counter)
                print('[+]')
                #time.sleep(1)
    p.add_date()
    del p


#===============================================IRR.RU============================================
#------------------------------------------------FLAT---------------------------------------------
    

def irr(maxprice):
    def get_html(url):
        r = requests.get(url)
        return r.text


    def get_page_data(html, url):
        soup = BeautifulSoup(html, 'lxml')

        print(url)
        #metro
        try:
            metro = []
            temp = soup.find('div', class_='irrSite__layout').find('div',
                class_='irrSite__wrapper').find_all('div',
                class_='siteBody__inner')[1].find('main', class_='siteBody__mainPart').find('div',
                class_='productPage__metro').text.split("м.")[1][1:].replace('\n','')
            metro.append(temp)
        except:
            metro = []  

        #pics
        pics = []          
        temp = soup.find('div', class_='irrSite__wrapper').find('div', class_='lineGallery').find_all('meta',itemprop="image")
        for i in temp:
            pics.append(i.get('content'))

        start = html.find('retailrocket.products.post')+28
        ch = '{'
        i = 0
        while ch != '}':
            ch = html[start+i]
            i+=1
        end = start + i
        data = json.loads(html[start:end] + '}')

        #descr
        descr = data["description"].replace(r'\n','')

        #area
        area = data["params"]["meters-total"]

        #cost
        cost = data["params"]["price"]

        #date
        date = data["params"]["date_create"].split()[0].split('-')
        date = '.'.join(list(reversed(date)))

        #id
        id = data["id"]

        #adr
        adr = soup.find("div", class_="siteBody").find_all("div", class_="siteBody__mainContainer")[1].find("div", class_="productPage__mainInfoWrapper").find("div", class_="productPage__infoTextBold js-scrollToMap").text.strip()

        #phone
        data_phone = soup.find("div", class_="siteBody").find_all("div", class_="siteBody__mainContainer")[1].find("div", class_="productPage__mainInfoWrapper").find("div", class_="productPage__phoneText").get("data-phone")
        phone = base64.b64decode(data_phone).decode("utf-8")
        contacts = {"phone": phone}

        #room_num
        temp = soup.find('div', class_='irrSite__layout').find('div',
            class_='irrSite__wrapper').find_all('div',
                class_='siteBody__inner')[1].find('main', class_='siteBody__mainPart').find('div',
                class_='productPage__infoColumn').find('ul').find_all('li', class_='productPage__infoColumnBlockText')#[2].text.split(':')[1])

        for i in range(len(temp)):
            if 'Комнат в квартире' in temp[i].text:
                room_num = int(temp[i].text.split(':')[1])
                break


        out = {"metro": metro, "descr": descr, "area": area, "cost": cost, "date": date, "adr": adr, "contacts": contacts, "room_num": room_num, "pics": pics, "url": url}
        return out


    def get_total_pages(html):
        soup = BeautifulSoup(html, 'lxml')
        total_pages = soup.find("div", class_="irrSite__layout js-irrSiteLayout js-favoriteAdd").find("div", class_="pagination js-paginationBlockHolder").find_all("li", class_="pagination__pagesItem")[-1].find("a").text
        return int(total_pages)


    def realestate(maxprice):
        maxprice = int(maxprice) // 1000
        p = Parse('irr')
        maxprice = 30 # Указывать в тясячах
        template = r"http://irr.ru/real-estate/rent/moskva-region/moskva-gorod/search/boundary_in_rooms=2,1,3/price=%20%D0%B4%D0%BE%20" + str(maxprice) + "%20000/rent_period=3674653711/page"
        base_url = r"http://irr.ru/real-estate/rent/moskva-region/moskva-gorod/search/boundary_in_rooms=2,1,3/price=%20%D0%B4%D0%BE%20" + str(maxprice) + "%20000/rent_period=3674653711/"
        #url = 'http://irr.ru/real-estate/apartments-sale/secondary/3-komn-kvartira-kovrovyy-mkr-advert642695870.html'
        html = get_html(base_url)
        out_data = []
        total_pages = get_total_pages(html)
        for page in range(total_pages)[1:]:
            url = template + str(page) + "/"
            html = get_html(url)
            soup = BeautifulSoup(html, 'lxml')
            ads = soup.find("div", class_="irrSite__wrapper").find("div", class_="siteBody__mainContainer").find("div", class_="listing").find_all("div", class_="listing__item")
            for ad in ads:
                try:
                    page_url = ad.find("div", class_="listing__itemTitleWrapper").find("a", class_="listing__itemTitle").get("href")
                    data = get_page_data(get_html(page_url), page_url)
                    p.append(data)
                    p.write_status(page)
                    print("Current_page: " + str(page))
                except:
                    alertExc()

        p.add_date()
        del p

    realestate(maxprice)


#---------------------------------------------------ROOMS-------------------------------------------------------


def irr_room():

    def get_html(url):
        r = requests.get(url)
        return r.text


    def get_page_data(html, url):
        soup = BeautifulSoup(html, 'lxml')

        print(url)
        #metro
        try:
            metro = []
            temp = soup.find('div', class_='irrSite__layout').find('div',
                class_='irrSite__wrapper').find_all('div',
                class_='siteBody__inner')[1].find('main', class_='siteBody__mainPart').find('div',
                class_='productPage__metro').text.split("м.")[1][1:].replace('\n','')
            metro.append(temp)
        except:
            metro = []  

        #pics
        pics = []          
        temp = soup.find('div', class_='irrSite__wrapper').find('div', class_='lineGallery').find_all('meta',itemprop="image")
        for i in temp:
            pics.append(i.get('content'))

        start = html.find('retailrocket.products.post')+28
        ch = '{'
        i = 0
        while ch != '}':
            ch = html[start+i]
            i+=1
        end = start + i
        data = json.loads(html[start:end] + '}')


        #descr
        descr = data["description"].replace(r'\n','')

        #area
        area = 'NULL'
        try:
            temp  = soup.find_all("div", class_="siteBody__inner")[1].find("div", class_="productPage__infoColumns").find("ul").find_all("li", class_="productPage__infoColumnBlockText")
            for i in temp:
                if "Площадь арендуемой комнаты:" in i.text:
                    area = i.text.split(":")[1].strip().split()[0]
                    break
        except:
            area = 0



        #cost
        try:
            cost = data["params"]["price"]
        except:
            return False


        #date
        date = data["params"]["date_create"].split()[0].split('-')
        date = '.'.join(list(reversed(date)))

        #id
        id = data["id"]

        #adr
        adr = soup.find("div", class_="siteBody").find_all("div", class_="siteBody__mainContainer")[1].find("div", class_="productPage__mainInfoWrapper").find("div", class_="productPage__infoTextBold js-scrollToMap").text.strip()

        #phone
        data_phone = soup.find("div", class_="siteBody").find_all("div", class_="siteBody__mainContainer")[1].find("div", class_="productPage__mainInfoWrapper").find("div", class_="productPage__phoneText").get("data-phone")
        phone = base64.b64decode(data_phone).decode("utf-8")
        contacts = {"phone": phone}

        #room_num
        room_num = 0


        out = {"metro": metro, "descr": descr, "area": area, "cost": cost, "date": date, "adr": adr, "contacts": contacts, "room_num": room_num, "pics": pics, "url": url}
        return out


    def get_total_pages(html):
        soup = BeautifulSoup(html, 'lxml')
        total_pages = soup.find("div", class_="irrSite__layout js-irrSiteLayout js-favoriteAdd").find("div", class_="pagination js-paginationBlockHolder").find_all("li", class_="pagination__pagesItem")[-1].find("a").text
        return int(total_pages)


    def realestate():
        p = Parse('irr')
        counter = 0
        maxprice = 15 # Указывать в тясячах
        template = r"http://irr.ru/real-estate/rooms-rent/moskva-region/moskva-gorod/search/price=%20%D0%B4%D0%BE%2030%20000/page"
        base_url = r"http://irr.ru/real-estate/rooms-rent/moskva-region/moskva-gorod/search/price=%20%D0%B4%D0%BE%2030%20000/"
        #url = 'http://irr.ru/real-estate/apartments-sale/secondary/3-komn-kvartira-kovrovyy-mkr-advert642695870.html'
        html = get_html(base_url)
        out_data = []
        total_pages = get_total_pages(html)
        for page in range(total_pages)[1:]:
            url = template + str(page) + "/"
            html = get_html(url)
            soup = BeautifulSoup(html, 'lxml')
            ads = soup.find("div", class_="irrSite__wrapper").find("div", class_="siteBody__mainContainer").find("div", class_="listing").find_all("div", class_="listing__item")
            for ad in ads:
                try:
                    page_url = ad.find("div", class_="listing__itemTitleWrapper").find("a", class_="listing__itemTitle").get("href")
                    data = get_page_data(get_html(page_url), page_url)
                    if data:
                        #print(data)
                        counter += 1
                        p.append(data)
                        p.write_status(counter)
                    #print(data)
                    #print("Current_page: " + str(page))
                except:
                    alertExc()

        p.add_date()
        del p

    realestate()


         
#===================================================================================================#
                                    # WORKING WITH SOCIAL NETWORKS #
#================================================VK=================================================#

PRIORITY_CRITEREA = ["без комиссии", "без посредников", "сам", "самостоятельно", "на длительный срок", "долгосрочн", "долгий", "собственник"]
METRO_PRIORITY = ["у", "возле", "рядом", "недалеко", "поблизости"]

def set_priority(descr):
    
    for cret in PRIORITY_CRITEREA:
        if cret in descr.lower():
            return "----!PRIORITY!----\n"+descr
    for cret in METRO_PRIORITY:
        if (cret+" метро") in descr.lower():
            return "----!PRIORITY!----\n"+descr
    
    return descr


def getVkId(offer):
    vkid = offer['from_id']
    if vkid < 0:
        return "http://vk.com/club"+str(-vkid)
    return "http://vk.com/id"+str(vkid)


def picsarr(offer):
    parr = []
    try:
        pics = offer['attachments']
        #print(len(pics))
        for pic in pics:
            if pic['type'] == "photo":
                picurl = pic['photo']['src_big']
                parr.append(picurl)
    except:
        #alertExc()
        pass
    return parr



def vk(n):        

    def parse_vk_community(community, n):
        
        counter = 0
        c = community['id']
        p = Parse(community['name'])
        for i in range(0, n, 100):
            offset = str(i)
            adr = "https://api.vk.com/method/wall.get?owner_id=-%s&count=100&filter=all&access_token=732c7b09732c7b09732c7b090673709b7f7732c732c7b092a6093eafb623ad5547f142f&offset=%s" % (c, offset)
            print(adr)
            offers = json.loads(requests.get(adr).text)
            offers = offers['response']
            for offer in offers[1:]:
                try:
                    counter += 1
                    p.write_status(counter)
                    p.append({'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0, 'room_num': 0, 'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)}, 'pics': picsarr(offer), 'descr': set_priority(offer['text']), 'metro': ['---'], 'url': "https://vk.com/wall-%s_%s" % (c, str(offer['id'])), 'loc': "-.-", 'adr': 'no_adress'}, useHash=True)
                except Exception as e:
                    alertExc()
                    #pass
        p.add_date()
        del p

    
    COMMUNITIES = [{'id': '1060484', 'name': "sdamsnimu"}, {'id': '29403745', 'name': "sdatsnyat"}, {'id': '62069824', 'name': "rentm"}, {'id': '49428949', 'name': "novoselie"}]
    
    for community in COMMUNITIES:
        #threading.Thread(target=parse_vk_community, args=(community, n,)).start()
        parse_vk_community(community, n)
        print("!!!!!!!!!!!!!1NOW WE PARSE",community)


#=================================SEARCH VK FEED====================================

SEARCH_PARS = ["квартиру", "комнату", "покомнатно", "койко место"]
WISHES = ["сдам ", "сниму "]

def vkfeed(n):
    p = Parse('vkfeed')
    counter = 0
    for par in SEARCH_PARS:
        for wish in WISHES:
            query = wish + par
            
            for i in range(0, n, 100):
                offset = str(i)
                adr = "https://api.vk.com/method/newsfeed.search?q=%s&count=100&access_token=732c7b09732c7b09732c7b090673709b7f7732c732c7b092a6093eafb623ad5547f142f&offset=%s" % (query, offset)
                print(adr)
                news = json.loads(requests.get(adr).text)['response']
                #print(news)
                
                for offer in news[1:]:
                    try:
                        counter += 1
                        p.write_status(counter)
                        if wish == 'сдам ':
                            p.append({'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0, 'room_num': 0, 'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)}, 'pics': picsarr(offer), 'descr': set_priority(offer['text']), 'metro': ['---'], 'url': "https://vk.com/wall%s_%s" % (str(offer['owner_id']), str(offer['id'])), 'loc': "-.-", 'adr': 'no_adress'}, useHash=True)
                        else:
                            p.append_snimu({'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0, 'room_num': 0, 'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)}, 'pics': picsarr(offer), 'descr': set_priority(offer['text']), 'metro': ['---'], 'url': "https://vk.com/wall%s_%s" % (str(offer['owner_id']), str(offer['id'])), 'loc': "-.-", 'adr': 'no_adress'})
                           
                    except Exception as e:
                        alertExc()
                        pass
                    
    p.add_date()
    del p
    
#===========================================OPTIMIZATION============================================#

#@tgExcCatch
def parse_it(name, maxprice):
    if name == 'cian':
        cian(maxprice)
    elif name == 'realEstate':
        realestate(maxprice)
    elif name == 'kvartirant':
        kvartirant_room()
        #alertBot.sendMessage("ROOOM STAGE FINISHED!")
        kvartirant(maxprice)
    elif name == 'rentooki':
        parse_rentookiru(maxprice)
    elif name == 'bezPosrednikov':
        bez_posrednikov(maxprice)
    elif name == 'posrednikovNet':
        posrednikovnetSdam()
        posrednikovnetSnimu()
    elif name == 'irr':
        irr(maxprice)
        irr_room()
    elif name == 'vk':    # maxprice stands for posts number
        vkfeed(maxprice)
        vk(maxprice)

    upload_db()


if __name__ == "__main__":
    vk(100)

