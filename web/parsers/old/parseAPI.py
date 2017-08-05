# This Python file uses the following encoding: utf-8

#===============================================IRR.RU============================================
#------------------------------------------------FLAT---------------------------------------------
    


#---------------------------------------------------ROOMS-------------------------------------------------------



         
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

