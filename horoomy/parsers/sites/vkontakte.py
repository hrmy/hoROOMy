# This Python file uses the following encoding: utf-8

import re
import json
import requests
from . import *


ALL_METROS_URL = "https://api.superjob.ru/2.0/suggest/town/4/metro/all/"

ALL_METROS = requests.get(ALL_METROS_URL).text
ALL_METROS = json.loads(ALL_METROS.lower()).get("objects", [])

ERROR_FILE = open("error_file.txt", 'w', encoding="utf-8")

OFFERS = json.loads(open("offers-sdam.json", 'r', encoding='utf-8').read().replace("\n", " "))
OFFERS.append(json.loads(open("offers-snimu.json", 'r', encoding='utf-8').read().replace("\n", " ")))

# ------------------------------------------REGEXPS----------------------------------------------------

# owner or renter
ownerExp = re.compile(r"сда[мюеё]|подсел")
renterExp = re.compile(r"сн(им[уеа]|ять)")

# urls
urlExp = re.compile(
    r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")

# phone
phonExp = re.compile(r"[87]?_{,3}\d{3}_{,3}\d{3}_{,3}\d{2}_{,3}\d{2}")

# preparing contents
prepareExp = re.compile(r"\W")
spacesExp = re.compile(r" {2,}")

# cost
costExp = re.compile(r"(\D\d{1,2} ?)((\d{3}\D)|т)")

# adress
adrExp = re.compile(r"((адресу?)|(ул(ица)?)) (.*){1,2} (д(ом)?)? \d{1,3} ?к? ?\d{,2}")

# area
#areaExp = re.compile(r"(общ(ей|ая)?)? ?(жил(ая|ой)?)? ?(площад[ьи]ю?)? ?\d\d ?([mм] ?2|кв м)?")
areaExp = re.compile(r"\D(площад[ьи]ю?)? ?\d\d ?(([mм] ?2)|(кв м))?\D")

# room number
room1Exp = re.compile(r"(одно ?ком)|(1 ?комн)")
room2Exp = re.compile(r"(двух? ?ком)|(2 ?комн)")
room3Exp = re.compile(r"(тр[ёе]х ?ком)|(3 ?комн)")

# whether the offer is about a flat or a room
roomExp = re.compile(r"комнат[ау]")
bedExp = re.compile(r"койк")
# -----------------------------------------------------------------------------------------------------


class SocialOffer:
    type = "owner/renter/error"
    cost = None
    room_num = None
    phone = ""
    links = []
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

        try:
            contents = re.sub(prepareExp, " ", raw_contents).lower()
            contents = re.sub(spacesExp, " ", contents)
            self.prepared_contents = contents
            return contents
        except:
            print(raw_contents)
            self.raise_error("Some error in preparing contents")

    # metro - also check whether the flat is in msk
    def get_metro(self):
        for m in ALL_METROS:
            if m['title'] in self.prepared_contents:
                self.metro = m['title']
                return m['title']

        self.metro = "No metro"
        return None

    # cost
    def get_cost(self):
        cost = re.search(costExp, self.prepared_contents)

        if cost is not None:
            cost = cost.group()

            if 'т' in cost:
                cost += '000'
            cost = int(re.sub(r"\D", "", cost))

            #while len(str(cost)) > 5:
            #    cost //= 1000

            self.cost = cost
            return cost

        self.cost = None
        return None

    # address
    def get_adr(self):
        adr = re.search(adrExp, self.prepared_contents)
        if adr is not None:
            adr = adr.group()
            print(adr)
            self.adr = adr
        else:
            self.adr = "No address"
            print("ADRESS NOT FOUND ")

    def getAll_adr(self):
        return re.findall(adrExp, self.prepared_contents)

    # retrieve urls from text
    def get_urls(self):
        urls = re.findall(urlExp, self.prepared_contents)
        if urls:
            for url in urls:
                self.links.append(url)
                print(url)
            return urls

        self.urls = ["No urls"]
        return None

    # remove urls from text
    def remove_urls(self):
        self.raw_contents = re.sub(urlExp, "", self.raw_contents)

    # get phone
    def get_phone(self):
        phone = re.search(phonExp, self.prepared_contents)
        if phone is not None:
            re.sub(phonExp, "", offer)
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
        if notFlat:
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
            area = re.sub(r"(м ?2)|\D", 'z', area)
            self.area = area
            return area
        return None

    def __init__(self, raw_contents):
        self.raw_contents = raw_contents

        self.get_urls()
        self.remove_urls()
        contents = self.prepare_contents()
        is_owner = re.search(ownerExp, contents) is not None
        is_renter = re.search(renterExp, contents) is not None
        #self.is_owner = is_owner
        #self.is_renter = is_renter

        if (is_owner and is_renter) or not (is_owner or is_renter):
            self.raise_error("Cant get wtf this is")
        else:
            addresses = self.getAll_adr()
            addresses_len = len(addresses)
            if addresses_len > 1:
                self.raise_error("Too many addresses: %s" % addresses_len)
                return
            addresses.append("No adr")
            self.adr = addresses[0]
            self.get_metro()

            if is_owner:
                if self.metro is None:
                    self.raise_error("Owner, but no metro!")
                    return

                self.type = "owner"
                self.get_area()

            else:
                self.type = "renter"

            self.get_phone()
            self.get_cost()
            self.get_rooms()


if __name__ == "__main__":
    for offer in OFFERS:
        while type(offer) == type([]):
            offer = offer[0]

        offr = SocialOffer(offer)
        if offr.type != "error":
            print(offr.__dict__)
        else:
            print("---")



ACCESS_TOKEN = "732c7b09732c7b09732c7b090673709b7f7732c732c7b092a6093eafb623ad5547f142f"

COMMUNITIES = [{'id': '1060484', 'name': "sdamsnimu"}, {'id': '29403745', 'name': "sdatsnyat"},
               {'id': '62069824', 'name': "rentm"}, {'id': '49428949', 'name': "novoselie"}]

PRIORITY_KEYWORDS = ["без комиссии", "без посредников", "сам", "самостоятельно", "на длительный срок", "долгосрочн",
                     "долгий", "собственник"]
METRO_KEYWORDS = ["у", "возле", "рядом", "недалеко", "поблизости"]
SEARCH_KEYWORDS = ["квартиру", "комнату", "покомнатно", "койко место"]
WISH_KEYWORDS = ["сдам ", "сниму "]

ALL_OFFERS = []


def set_priority(descr):
    for kword in PRIORITY_KEYWORDS:
        if kword in descr.lower():
            return "----!PRIORITY!----\n" + descr
    for kword in METRO_KEYWORDS:
        if (kword + " метро") in descr.lower():
            return "----!PRIORITY!----\n" + descr

    return descr


def getVkId(offer):
    vkid = offer['from_id']
    if vkid < 0:
        return "http://vk.com/club" + str(-vkid)
    return "http://vk.com/id" + str(vkid)


def picsarr(offer):
    parr = []
    try:
        pics = offer['attachments']
        # print(len(pics))
        for pic in pics:
            if pic['type'] == "photo":
                picurl = pic['photo']['src_big']
                parr.append(picurl)
    except:
        # alertExc()
        pass
    return parr


def parse_vk_community(n=300):
    for community in COMMUNITIES:
        c = community['id']
        for i in range(0, n, 100):
            offset = str(i)
            adr = "https://api.vk.com/method/wall.get?owner_id=-%s&count=100&filter=all&access_token=%s&offset=%s" % (
                c, ACCESS_TOKEN, offset)
            print(adr)
            offers = requests.get(adr).json()
            ALL_OFFERS.append(offers['response'][1:])

            #for offer in offers[1:]:
                #yield {'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0, 'room_num': 0,
                #       'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)}, 'pics': picsarr(offer),
                #       'descr': set_priority(offer['text']), 'metro': ['---'],
                #       'url': "https://vk.com/wall-%s_%s" % (c, str(offer['id'])), 'loc': "-.-", 'adr': 'no_adress'}


# =================================SEARCH VK FEED====================================




def vkfeed(n=300):
    for par in SEARCH_KEYWORDS:
        for wish in WISH_KEYWORDS:
            query = wish + par

            for i in range(0, n, 100):
                offset = str(i)
                adr = "https://api.vk.com/method/newsfeed.search?q=%s&count=100&access_token=%s&offset=%s" % (
                query, ACCESS_TOKEN, offset)
                print(adr)
                news = requests.get(adr).json()['response'][1:]
                # print(news)
                ALL_OFFERS.append(news)

                # for offer in news[1:]:
                #         if wish == 'сдам ':
                #             yield {'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0,
                #                       'room_num': 0, 'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)},
                #                       'pics': picsarr(offer), 'descr': set_priority(offer['text']), 'metro': ['---'],
                #                       'url': "https://vk.com/wall%s_%s" % (str(offer['owner_id']), str(offer['id'])),
                #                       'loc': "-.-", 'adr': 'no_adress'}
                #         else:
                #
                #                 yield {'type': 'renter', 'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0,
                #                  'room_num': 0, 'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)},
                #                  'pics': picsarr(offer), 'descr': set_priority(offer['text']), 'metro': ['---'],
                #                  'url': "https://vk.com/wall%s_%s" % (str(offer['owner_id']), str(offer['id'])),
                #                  'loc': "-.-", 'adr': 'no_adress'}
import json
def parse():

    parse_vk_community()
    vkfeed()

    print(len(ALL_OFFERS))

    # f = open("somefile.txt", 'w', encoding='utf-8')
    # f.write(json.dumps(ALL_OFFERS, ensure_ascii=False))
    # f.close()

    #for offer in ALL_OFFERS:



if __name__ == "__main__":
    parse()