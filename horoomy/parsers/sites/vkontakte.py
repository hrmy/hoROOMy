from . import *
import requests


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

    f = open("somefile.txt", 'w', encoding='utf-8')
    f.write(json.dumps(ALL_OFFERS, ensure_ascii=False))
    f.close()

    #for offer in ALL_OFFERS:



if __name__ == "__main__":
    parse()