# This Python file uses the following encoding: utf-8

import math
import json
import threading
from multiprocessing import Process
from parseAPI import parse_it
from bottle import *
from parser_class import Parse
from database import DataBase, DBcon
from botApi import tgExcCatch, alertExc
from driveAPI import upload_db


# return an html page
def html(filename):
    return static_file(filename+'.html', root='./html')


# мегакостыль для авторизации (как пропишем авторизацию, уберём его)
def auth_func(uname, pw):
    if uname == 'admin' and pw == 'adminpsw':
        return True
    return False


#-------------------------before run------------------------

# all parser names are kept in json file
PARSER_LIST = json.loads(open('parser_list.json', 'r').read())

# get stuff like version and description if exists
try:
    FORMAT_DIC = json.loads(DBcon.fetch("SELECT * FROM alerts;")[0][0][1:-1])
except:
    FORMAT_DIC = {'version': 'unknown', 'added': '---', 'othertext': ''}

# creating all status rows - needs to be rewritten
for p in PARSER_LIST:
    parsr = Parse(p)
    try:
        if parsr.get_status() == ' ':
            parsr.write_status('last updated on: never')
    except:
        parsr.write_status('last updated on: never')
        
    del parsr

    

#===========================server is here============================


# main page
@get("/")
def main():
    redirect('/search')


#-------------------------PARSER CONTROL PANEL------------------------


# html
@get("/system")
@auth_basic(auth_func)
def ss():
    return template("./html/main.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


# html with version-control cms
@get("/adm/main")
def main():
    return template("./html/main-adm.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


# processing to change cms info
@get("/changemain")
def change():
    for param in request.query:
        if request.query[param] != "":
            FORMAT_DIC[param] = request.query[param]
    DBcon.delete_table('alerts') # clear alerts
    cmnd = """INSERT INTO alerts VALUES ('''%s''');""" % str(json.dumps(FORMAT_DIC, ensure_ascii=False))
    print(cmnd)
    DBcon.query(cmnd)
    redirect("/adm/main")


#-------------------------------ACTIVATE PARSERS------------------------------
    

# start parsing social networks
@get("/start_social")
def st():
    n = int(request.query.num)
    t = threading.Thread(target=parse_it, args=('vk', n,))
    t.daemon = True
    t.start()
    redirect("/")


# start parse (ALL parsers)
@get("/start_parse")
#@tgExcCatch
def st():              
    maxprice = request.query.maxprice
    #DBcon.delete_table('Results')
    for parser_name in PARSER_LIST:
        t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))    	
        t.daemon = True
        t.start()
    redirect("/")
    

# start parse (ONE parser)
@get("/special_parse")
def spp():
    #maxprice = int(request.query.maxprice)
    maxprice = 15000
    parser_name = request.query.parser_name
    t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))
    t.daemon = True
    t.start()
    redirect('/')


#---------------------------------RESULTS & STATUSES------------------------------


# clear tables with parsing results
@get("/clear_results")
def clear():
    DBcon.delete_table('Results')
    DBcon.delete_table('Snimu')
    #db.format()
    redirect('/')


# get parsed results
@get("/res/<parser>")
def res(parser):
    return Parse(parser).get_results()


# get stats for a parser
@get("/parse_status/<parser>")
def return_status(parser):
    #resp.set_header("Cache-Control", 'no-store, no-cache, must-revalidate, max-age=0')
    return Parse(parser).get_status()


# all parsers list
@get("/plist")
def pl():
    return json.dumps(PARSER_LIST)


# download db
@get("/db")
def db():
    return static_file("parseRes.db", root='.', download=True)


#------------------------------------USER EXPERIENCE---------------------------------


# search flats html
@get("/search")
def search():
    return html('search')


# returns search results
@get("/giveMeFlats")
def give():

    def cost_range(a):  # cost range formula
        if a != '':
            a = int(a)
            b = int()
            b = math.trunc(40*math.sqrt(a))
            return a-b, a+b     # min_cost, max_cost
        else:
            return 0, 100000
    
    q = request.query

    # room_num
    if q['dealType'] == "Flat":
        room_num = '=' + q['room_num']
        if room_num == '=':
            room_num = ' IN (1, 2, 3)'
    else:
        room_num = '=0'

    # page
    if 'page' not in q:
        offset = 0
    else:
        offset = (int(q['page'])-1) * 20

    # cost
    min_cost, max_cost = cost_range(q['cost'])

    cmnd = "FROM Results WHERE cost BETWEEN %s AND %s " % (min_cost, max_cost)
    
    # metro
    if q['metro'] != '':
        metro = q['metro'].encode('ISO-8859-1').decode('utf-8')
        cmnd += "AND metro LIKE '%%%s%%' " % metro
        
    cmnd += """    
AND room_num%s""" % room_num
        
    DBcon.query('PRAGMA case_sensitive_like = FALSE;')

    # offers count
    cmnd_count = "SELECT count(*) " + cmnd
    # offers text
    cmnd = "SELECT prooflink, pics, cost, room_num, area, contacts, loc, adr, date, descr " + cmnd + " LIMIT 20 OFFSET %s;" % offset

    res = DBcon.fetch(cmnd)
    count = DBcon.fetch(cmnd_count)[0][0]
    print(count)

    res = json.dumps(res).replace('(', '[').replace(')', ']')

    # insert all flats json into JS template
    return open('./html/tableRes.html', 'r', encoding='windows-1251').read().replace('{{{cnt}}}', str(count)).replace('{{{offr}}}', res).encode('windows-1251')



@get("/giveMePosts/<category>")
def posts(category):
    if 'num' in request.query and num != "":
        cmnd = " LIMIT " + str(request.query['num']) + ";"
    else:
        cmnd = ";"
        
    if category == "sdam":
        fetch_cmnd = "SELECT descr FROM Results WHERE fromwhere in ('vkfeed', 'novoselie', 'rentm', 'sdamsnimu', 'sdatsnyat')" + cmnd
    else:
        if category != "snimu":
            return HTTPError(500, "Wrong request to hoROOMy parsers API")
        fetch_cmnd = "SELECT descr FROM Snimu"+cmnd

    return json.dumps(DBcon.fetch(fetch_cmnd), ensure_ascii=False)
        
#----------------------------------------MAP----------------------------------------------

#костыль с записью в текстовый файл. NEEDES TO BE IMPROVED

@get("/geolocate")
def geo():
    if request.query['loc'] == "YANDEXLOCERR":
        return '<h2>К сожалению, мы не можем найти что-либо по указанному адресу :( </h2>'
    lat, lng =  request.query['loc'].split(',')
    locvar = open("locvar_storage.js", 'w')
    towrite = """var get_lat = %s
var get_lng = %s
var get_rad = 80""" % (lat, lng)
    locvar.write(towrite)
    locvar.close()
    return html("circler")


@get("/locvar_storage.js")
def locvar():
    return static_file('/locvar_storage.js', root='.')



#----------------------------------------------------------------------------------------------------


# get any image
@get("/pics/<filename>")
def pics(filename):
    return static_file(filename, root='./pics')


# get stats for a metro station
@get("/stats")
def stats():
    return html("stats")


# retrieve stats from the db
@get("/giveMeStats")
def stats():
    metro = request.query.metro

    try:
        room = DBcon.fetch("SELECT avg(room_num) FROM Results WHERE metro like '%%%s%%';" % metro)[0][0]
        room = str(room)[:str(room).find('.')+4]
    except:
        room = 'undefined'

    try:
        cost = DBcon.fetch("SELECT AVG(cost) FROM Results WHERE metro like '%%%s%%';" % metro)[0][0]
        cost = str(cost)[:str(cost).find('.')]
    except:
        cost = 'undefined'

    try:
        area = DBcon.fetch("SELECT AVG(area) FROM Results WHERE metro like '%%%s%%';" % metro)[0][0]
        area = str(area)[:str(area).find('.')]
    except:
        area = 'undefined'

    return template('./html/giveMeStats.html', metro=metro, room=room, cost=cost, area=area)


# upload db to dropbox
@get("/sync_db")
def snc():
    #try:
    upload_db()
    redirect('/system')
    #except:
     #   alertExc()
     

# styles
@get("/css/style.css")
def css():
    return static_file('style.css', root='./css')



# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
