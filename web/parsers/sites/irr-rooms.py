from . import *

def get_html(url):
    r = requests.get(url)
    return r.text


def get_page_data(html, url):
    soup = BeautifulSoup(html, 'lxml')

    print(url)
    # metro
    try:
        metro = []
        temp = soup.find('div', class_='irrSite__layout').find('div',
                                                               class_='irrSite__wrapper').find_all('div',
                                                                                                   class_='siteBody__inner')[
                   1].find('main', class_='siteBody__mainPart').find('div',
                                                                     class_='productPage__metro').text.split("м.")[1][
               1:].replace('\n', '')
        metro.append(temp)
    except:
        metro = []

    # pics
    pics = []
    temp = soup.find('div', class_='irrSite__wrapper').find('div', class_='lineGallery').find_all('meta',
                                                                                                  itemprop="image")
    for i in temp:
        pics.append(i.get('content'))

    start = html.find('retailrocket.products.post') + 28
    ch = '{'
    i = 0
    while ch != '}':
        ch = html[start + i]
        i += 1
    end = start + i
    data = json.loads(html[start:end] + '}')

    # descr
    descr = data["description"].replace(r'\n', '')

    # area
    try:
        temp = soup.find_all("div", class_="siteBody__inner")[1].find("div", class_="productPage__infoColumns").find(
            "ul").find_all("li", class_="productPage__infoColumnBlockText")
        for i in temp:
            if "Площадь арендуемой комнаты:" in i.text:
                area = i.text.split(":")[1].strip().split()[0]
                break
    except:
        area = None

    # cost
    try:
        cost = data["params"]["price"]
    except:
        return False

    # date
    date = data["params"]["date_create"].split()[0].split('-')
    date = '.'.join(list(reversed(date)))
    date = datetime.strptime(date, '%d.%m.%Y')

    # id
    id = data["id"]

    # adr
    adr = soup.find("div", class_="siteBody").find_all("div", class_="siteBody__mainContainer")[1].find("div",
                                                                                                        class_="productPage__mainInfoWrapper").find(
        "div", class_="productPage__infoTextBold js-scrollToMap").text.strip()

    # phone
    data_phone = soup.find("div", class_="siteBody").find_all("div", class_="siteBody__mainContainer")[1].find("div",
                                                                                                               class_="productPage__mainInfoWrapper").find(
        "div", class_="productPage__phoneText").get("data-phone")
    phone = base64.b64decode(data_phone).decode("utf-8")
    contacts = {"phone": phone}

    # room_num
    room_num = 0

    out = {"metro": metro, "descr": descr, "area": area, "cost": cost, "date": date, "adr": adr, "contacts": contacts,
           "room_num": room_num, "pics": pics, "url": url}
    return out


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    total_pages = soup.find("div", class_="irrSite__layout js-irrSiteLayout js-favoriteAdd").find("div",
                                                                                                  class_="pagination js-paginationBlockHolder").find_all(
        "li", class_="pagination__pagesItem")[-1].find("a").text
    return int(total_pages)


def parse(**kwargs):
    logger = kwargs['logger']

    template = r"http://irr.ru/real-estate/rooms-rent/moskva-region/moskva-gorod/search/price=%20%D0%B4%D0%BE%2030%20000/page"
    base_url = r"http://irr.ru/real-estate/rooms-rent/moskva-region/moskva-gorod/search/price=%20%D0%B4%D0%BE%2030%20000/"
    #url = 'http://irr.ru/real-estate/apartments-sale/secondary/3-komn-kvartira-kovrovyy-mkr-advert642695870.html'
    html = get_html(base_url)
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
                    yield data

            except:
                logger.error("irr-rooms Error")
