from . import *


def parse(**kwargs):
    maxprice = int(kwargs.get('maxprice', 55000))
    logger = kwargs['logger']

    # Iterate page indexes
    page_index = 1
    while True:
        # Get page
        offers_page_html = requests.get("http://rentooki.ru/moscow/?page={0}".format(page_index)).text
        offers_page = BeautifulSoup(offers_page_html, "lxml")

        # Extract offer links
        links = offers_page.find_all("a", class_="pull-left relative", href=True)
        links = [x["href"] for x in links]

        # Exit on end
        if "Следующая" not in offers_page_html:
            logger.warning("Stopping parsing RENTOOKI, no nextpage found!")
            break

        for link in links:
            try:

                # Get offer page
                offer_page = BeautifulSoup(requests.get("http://rentooki.ru{0}".format(link)).text, "lxml")

                # Extract title info
                title = offer_page.find("h2").contents[0]
                title = " ".join(title.split())

                # Split title to fields
                try:
                    offer_type_field, area_field, floor_field = title.split(",")
                except:
                    continue

                # Placement date
                datetime_field = offer_page.find("small").contents[0].replace("Размещено", "").strip()
                try:
                    dt = datetime.strptime(datetime_field, "%d %b %H:%M")
                    dt = dt.replace(year=datetime.now().year)
                    print(dt)
                except:
                    if "cегодня" in datetime_field:
                        datetime_field = re.match(r".+ (\d+:\d+)", datetime_field).group(1)
                        dt = datetime.strptime(datetime_field, "%H:%M")
                        dt = datetime.now().replace(hour=dt.hour, minute=dt.minute)
                    elif "вчера" in datetime_field:
                        datetime_field = re.match(r".+ (\d+:\d+)", datetime_field).group(1)
                        dt = datetime.strptime(datetime_field, "%H:%M")
                        dt = datetime.now().replace(hour=dt.hour, minute=dt.minute)
                        dt = dt - timedelta(days=1)
                    else:
                        continue

                # Extract rooms number
                room_number = list(str(offer_type_field).split(" "))[2]
                if room_number != 'комната':
                    room_number = int(room_number[0])
                else:
                    room_number = 0
                # Extract area
                area = int(re.match(r"(\d+)", area_field.strip()).group(1))
                # Extract floor
                floor = int(re.match(r"(\d+)/", floor_field.strip()).group(1))

                # Cost and phone
                list_group = offer_page.find_all("li", class_="list-group-item")
                cost = int(list_group[0].next_element.next_element.contents[0].replace(" ", ""))
                if int(cost) > maxprice:
                    print("!!!MORE THAN MAXPRICE!!!")
                    continue
                # adr = list_group[1].contents[0].replace("\n", "").strip()
                descr = list_group[2].next_element.contents[0]
                contact_phone = list_group[4].next_element
                a = list(str(list_group[1].text).split("\n"))
                adr = "Москва, " + a[1].strip()
                metro = [a[0][a[0].find(" "):].strip()]

                # Pics
                images = offer_page.find_all("img", class_="img-responsive center-block")
                images = ["http://rentooki.ru" + x["src"] for x in images]

                # Group parsed data
                offer = {
                    "type": "owner",
                    "url": "http://rentooki.ru" + link,
                    "room_num": room_number,
                    "area": area,
                    "floor": floor,
                    "cost": cost,
                    "contacts": {"phone": contact_phone},
                    "metro": metro,
                    "pics": images,
                    "date": dt,
                    "adr": adr,
                    "loc": None,
                    "descr": descr
                }

                logger.info("One more owner with Rentooki")
                yield offer
            except:
                logger.error("Some error in Rentooki, no traceback yet")

            # Next page on next iteration
            page_index += 1

