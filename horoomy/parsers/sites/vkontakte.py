# This Python file uses the following encoding: utf-8

from . import *

# =====================================REGULAR EXPRESSIONS==============================================

ALL_METROS_URL = "https://api.superjob.ru/2.0/suggest/town/4/metro/all/"

ALL_METROS = requests.get(ALL_METROS_URL).text
ALL_METROS = json.loads(ALL_METROS.lower()).get("objects", [])

# ------------------------------------------REGEXPS----------------------------------------------------

# owner or renter
ownerExp = re.compile(r"сда[мюеё]|подсел|освобо")
renterExp = re.compile(r"сн(им[уеа]|ять)|ищ(у|ем) ")

# urls
urlExp = re.compile(
    r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")

# phone
phonExp = re.compile(r"[87]? ?\d{3} ?\d{3} ?\d{2} ?\d{2}")

# preparing contents
prepareExp = re.compile(r"\W")
spacesExp = re.compile(r" {2,}")

# cost
costExp = re.compile(r"(\D\d{1,2} ?)((\d{3}\D)|т((ыс)| ?р))")

# address
adrExp = re.compile(r"((адресу?)|(ул(ица)?)) (\w*) (д(ом)?)? \d{1,3} ?к?(орпус)? ?\d{,2}?")

# area
areaExp = re.compile(r"\D(общ(ей|ая)?)?(площад[ьи]ю?)? ?\d\d ?(([mм] ?2)|(кв м))\D")

# room number
room1Exp = re.compile(r"(одно ?ком)|(1 ?комн)")
room2Exp = re.compile(r"(двух? ?ком)|(2[ х]{,3}комн)")
room3Exp = re.compile(r"(тр[ёе]х ?ком)|(3[ х]{,3}комн)")

# whether the offer is about a flat or a room
roomExp = re.compile(r"комнат[ау]")
bedExp = re.compile(r"койк")
# -----------------------------------------------------------------------------------------------------


class SocialOffer:
    type = "owner/renter/error"
    cost = None
    room_num = None
    phone = ""
    urls = []
    raw_contents = ""
    prepared_contents = ""

    area = None
    metro = []
    adr = ""

    def raise_error(self, error_text="No description:("):
        self.type = "error"
        self.prepared_contents = error_text

    # prepare contents - remove punctuation in description to analise contents
    def prepare_contents(self, raw_contents=None):
        if raw_contents is None: raw_contents = self.raw_contents

        contents = re.sub(prepareExp, " ", raw_contents).lower()
        contents = re.sub(spacesExp, " ", contents)
        self.prepared_contents = contents
        return contents

    # metro - also check whether the flat is in msk
    def get_metro(self):
        metros = []
        for m in ALL_METROS:
            if m['title'] in self.prepared_contents:
                metros.append(m['title'])

        self.metro = metros

    # cost
    def get_cost(self):
        cost = re.search(costExp, self.prepared_contents)

        if cost is not None:
            cost = cost.group()
            self.logger.info(cost)

            if 'т' in cost:
                cost += '000'
            cost = int(re.sub(r"\D", "", cost))
            self.cost = cost
            return cost

        self.cost = None
        return None

    # address
    def get_adr(self):
        adr = re.search(adrExp, self.prepared_contents)
        if adr is not None:
            adr = adr.group()
            self.logger.info(adr)
            self.adr = adr

    def getAll_adr(self):
        return re.findall(adrExp, self.prepared_contents)

    # retrieve urls from text
    def get_urls(self):
        urls = re.findall(urlExp, self.raw_contents)
        if urls:
            self.urls = urls
            return urls

        self.urls = None
        return None

    # remove urls from text
    def remove_urls(self):
        self.raw_contents = re.sub(urlExp, "", self.raw_contents)

    # get phone
    def get_phone(self):
        phone = re.search(phonExp, self.prepared_contents)
        if phone is not None:
            self.prepared_contents = re.sub(phonExp, "", self.prepared_contents)
            phone = phone.group()
            self.phone = phone
            return phone
        else:
            self.phone = None

    def bed_or_room(self):
        if re.search(roomExp, self.prepared_contents):
            return 0
        elif re.search(bedExp, self.prepared_contents):
            return -1

    def get_rooms(self):
        notFlat = self.bed_or_room()
        self.logger.info(notFlat)
        if notFlat is not None:
            self.room_num = notFlat
            return notFlat
        else:
            for roomExp in enumerate([room1Exp, room2Exp, room3Exp]):
                room_num = re.search(roomExp[1], self.prepared_contents)
                if room_num is not None:
                    self.room_num = roomExp[0] + 1
                    return roomExp[0] + 1

    def get_area(self):
        area = re.search(areaExp, self.prepared_contents)
        if area is not None:
            area = area.group()
            area = int(re.sub(r"(м ?2)|\D", '', area))
            self.area = area
            return area

    def __init__(self, raw_contents, logger):
        self.logger = logger
        self.raw_contents = raw_contents

        self.get_urls()
        if self.urls:
            self.raise_error("Realtor filter -- suspicious urls")
            return

        if len(re.findall('<br>', self.raw_contents)) > 6:
            self.raise_error("Bullshit filter -- bad contents")
            return

        contents = self.prepare_contents()
        is_owner = re.search(ownerExp, contents) is not None
        is_renter = re.search(renterExp, contents) is not None

        if (is_owner and is_renter) or not (is_owner or is_renter):
            self.raise_error("Cant get wtf this is")
        else:
            self.get_adr()
            self.get_metro()

            if is_owner:
                if not self.metro:
                    self.raise_error("Owner, but no metro!")
                    return

                self.type = "owner"
                self.get_area()

            else:
                self.type = "renter"

            self.get_phone()
            self.get_cost()
            self.get_rooms()


# ==========================================VKONTAKTE PARSER==================================================

ACCESS_TOKEN = "732c7b09732c7b09732c7b090673709b7f7732c732c7b092a6093eafb623ad5547f142f"

COMMUNITIES = [{'id': '1060484', 'name': "sdamsnimu"},
               {'id': '29403745', 'name': "sdatsnyat"},
               {'id': '62069824', 'name': "rentm"},
               {'id': '49428949', 'name': "novoselie"}]

PRIORITY_KEYWORDS = ["без комиссии",
                     "без посредников",
                     "сам", "самостоятельно",
                     "на длительный срок",
                     "долгосрочн",
                     "долгий",
                     "собственник"]

METRO_KEYWORDS = ["у", "возле",
                  "рядом", "недалеко",
                  "поблизости"]

SEARCH_KEYWORDS = ["квартиру", "комнату",
                   "покомнатно", "койко место"]

WISH_KEYWORDS = ["сдам ", "сниму "]


def set_priority(descr):
    for keyword in PRIORITY_KEYWORDS:
        if keyword in descr.lower():
            return "----!PRIORITY!----\n" + descr
    for keyword in METRO_KEYWORDS:
        if (keyword + " метро") in descr.lower():
            return "----!PRIORITY!----\n" + descr

    return descr


def getVkId(offer):
    vk_id = offer['from_id']
    if vk_id < 0:
        return "http://vk.com/club" + str(-vk_id)
    return "http://vk.com/id" + str(vk_id)


def picsarr(offer):
    pics_arr = []
    pics = offer.get('attachments', [])

    for pic in pics:
        if pic['type'] == "photo":
            pic_url = pic.get('photo', dict()).get('src_big', None)
            if pic_url is not None:
                pics_arr.append(pic_url)

    return pics_arr


# =================================SEARCH VK FEED====================================

def parse(n=300, **kwargs):
    logger = kwargs.get('logger').channel('Vkontakte')
    logger.info('pars')

    for par in SEARCH_KEYWORDS:
        logger.info(par)
        for wish in WISH_KEYWORDS:
            query = wish + par

            for offset in range(0, n, 100):
                adr = "https://api.vk.com/method/newsfeed.search?q=%s&count=100&access_token=%s&offset=%s" % (
                    query, ACCESS_TOKEN, offset)
                logger.info(adr)

                news = requests.get(adr).json().get('response', None)
                if isinstance(news, list):
                    if len(news) > 1:
                        news = news[1:]

                for offer in news:
                    logger.info(type(offer))
                    if isinstance(offer, dict):
                        processed_offer = SocialOffer(offer.get('text', ''), logger)
                        if processed_offer.type != 'error':
                            yield {'type': processed_offer.type,
                                   'date': datetime.fromtimestamp(offer['date']),
                                   'cost': processed_offer.cost,
                                   'room_num': processed_offer.room_num,
                                   'area': processed_offer.area,
                                   'contacts': {'phone': processed_offer.phone, 'vk': getVkId(offer)},
                                   'pics': picsarr(offer),
                                   'descr': set_priority(processed_offer.raw_contents),
                                   'metro': processed_offer.metro,
                                   'url': "https://vk.com/wall%s_%s" % (str(offer['owner_id']), str(offer['id'])),
                                   'loc': None,
                                   'adr': processed_offer.adr}

    for community in COMMUNITIES:
        c = community['id']
        for offset in range(0, n, 100):
            adr = "https://api.vk.com/method/wall.get?owner_id=-%s&count=100&filter=all&access_token=%s&offset=%s" % (
                c, ACCESS_TOKEN, offset)
            logger.info(adr)
            offers = requests.get(adr).json().get('response', None)
            if isinstance(offers, list):
                if len(offers) > 1:
                    offers = offers[1:]

            for offer in offers:
                if isinstance(offer, dict):
                    processed_offer = SocialOffer(offer.get('text', ''), logger)
                    if processed_offer.type != 'error':
                        yield {'type': processed_offer.type,
                               'date': datetime.fromtimestamp(offer['date']),
                               'cost': processed_offer.cost,
                               'room_num': processed_offer.room_num,
                               'area': processed_offer.area,
                               'phone': processed_offer.phone,
                               'contacts': {'phone': processed_offer.phone, 'vk': getVkId(offer)},
                               'pics': picsarr(offer),
                               'descr': set_priority(processed_offer.raw_contents),
                               'metro': processed_offer.metro,
                               'url': "https://vk.com/wall-%s_%s" % (c, str(offer['id'])),
                               'loc': None,
                               'adr': processed_offer.adr}


if __name__ == "__main__":
    parse()
