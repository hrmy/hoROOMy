from . import *


def getsoup(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html5lib")
    return soup


def getarea(soup):
    area_info = soup.find("table", {"class": "object_descr_props"})
    if area_info is None:
        area = "No info"
        return area
    else:
        area_tr = area_info.findAll("tr")
        area = area_tr[2].text
        integ = []
        i = 0
        while i < len(area):
            area_int = ''
            a = area[i]
            while '0' <= a <= '9':
                area_int += a
                i += 1
                if i < len(area):
                    a = area[i]
                else:
                    break
            i += 1
            if area_int != '':
                integ.append(int(area_int))
        try:
            area = integ[0]
            return area
        except IndexError:
            area = "No info"
            return area


def getadr(soup):
    adr_info = soup.find("h1", {"class": "object_descr_addr"})
    if adr_info is None:
        adr = "Error"
        return adr
    else:
        adr = adr_info.text
        return adr


def getpics(soup):
    all_images = []
    infa = soup.find("div", {"class": "fotorama"})
    if infa == None:
        all_images = ["No Images"]
        return all_images
    else:
        images = infa.findAll("img")
        for i in images:
            x = i.get("src")
            all_images.append(x)
        return all_images


def getmetro(soup):
    all_metro = []
    metro_infa = soup.findAll("a", {"class": "object_item_metro_name"})
    if metro_infa is None:
        all_metro = ["No metro near"]
        return all_metro
    else:
        for i in metro_infa:
            metro = i.text[:-1]
            all_metro.append(metro)
            return all_metro


def getphone(soup):
    ph_infa = soup.find("div", {"class": "cf_offer_show_phone-number cf_offer_show_phone-number--under_price"})
    if ph_infa is None:
        phone = "No Phone"
        return phone
    else:
        phone = ph_infa.find("a").text
        return phone


def getdescr(soup):
    descr_info = soup.find("div", {"class": "object_descr_text"})
    if descr_info is None:
        descr = "No descr"
        return descr
    else:
        descr_info = str(descr_info)[1:]
        bord_r = descr_info.find("<")
        bord_l = descr_info.find(">")
        descr = descr_info[bord_l + 1:bord_r]
        return descr


def getpersonname(soup):
    person_name_info = soup.find("h3", {"class": "realtor-card__title"})
    if person_name_info is None:
        person_name = "no name"
        return person_name
    else:
        try:
            person_name = person_name_info.find("a").text
            return person_name
        except AttributeError:
            person_name = soup.find("h3", {"class": "realtor-card__title"}).text
            return person_name


def getposttime(soup):
    infa = soup.find("div", {"class": "object_descr_dt_row"})
    if infa is None:
        return datetime.today()
    else:
        try:
            posttime = str(infa.find("span", {"class": "object_descr_dt_added"}).a)
            posttime = json.loads(posttime[posttime.find('{'):posttime.rfind('}') + 1])['publication_date']
            posttime = gmtime(posttime)
            return posttime
        except AttributeError:
            return datetime.today()


def parse(**kwargs):
    logger = kwargs['logger']

    link_template = 'https://cian.ru/rent/flat/'
    url = [
        "https://map.cian.ru/ajax/map/roundabout/?currency=2&deal_type=rent&engine_version=2&type=-2&maxprice=35000&offer_type=flat&region=1&wp=1&room1=1&p=",
        "https://map.cian.ru/ajax/map/roundabout/?currency=2&deal_type=rent&engine_version=2&type=-2&maxprice=45000&offer_type=flat&region=1&wp=1&room2=1&p=",
        "https://map.cian.ru/ajax/map/roundabout/?currency=2&deal_type=rent&engine_version=2&type=-2&maxprice=55000&offer_type=flat&region=1&wp=1&room3=1&p="]
    for mainurl in url:
        for num in range(1, 6):
            url = mainurl + str(num)

            html = requests.get(url).text
            try:
                json_text = json.loads(html)
            except json.decoder.JSONDecodeError:
                logger.error("Cian: json error")
                break
            if "data" in json_text:
                infa = json_text["data"]
                if "points" in infa:
                    infa = infa["points"]
                    for i in infa:
                        main = infa[i]
                        offers = main["offers"]
                        for j in offers:
                            room_num = j['property_type']
                            price = int(j['price_rur'][:-2])
                            floor = j["link_text"][3]
                            floor = floor[floor.find(" ") + 1:]
                            flat_id = j["id"]
                        url = link_template + flat_id
                        loc = i.split()

                        soup = getsoup(url)
                        all_pics = getpics(soup)
                        all_metro = getmetro(soup)
                        phone = getphone(soup)
                        adr = getadr(soup)
                        area = getarea(soup)
                        descr = getdescr(soup)
                        person_name = getpersonname(soup)
                        date = getposttime(soup)

                        x = {'type': "owner", 'room_num': room_num, 'metro': all_metro, 'pics': all_pics,
                             "cost": price, "floor": floor,
                             "contacts": {"phone": phone, "person_name": person_name}, "loc": loc,
                             "url": url, "area": area, "adr": adr, "descr": descr, "date": date}

                        yield x
