
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


def parse(**kwargs):
    maxprice = kwargs.get('maxprice', 55000) // 1000
    logger = kwargs['logger']

    p = Parse('irr')
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
