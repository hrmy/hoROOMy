# This Python file uses the following encoding: utf-8

import math
import json
import threading
from parseAPI import parse_it
from bottle import *
from parser_class import Parse
from database import DataBase, DBcon
from botAPI import tgExcCatch, alertExc
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
@get("/system/edit")
def main():
    return template("./html/main-adm.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


# processing to change cms info
@get("/system/changemain")
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
@get("/parsers/start_social")
def st():
    if 'num' in request.query:
        n = int(request.query['num'])
    else:
        n = 100
    t = threading.Thread(target=parse_it, args=('vk', n,))
    t.daemon = True
    t.start()
    redirect("/")


# start parse (ALL parsers)
@get("/parsers/start_parse")
#@tgExcCatch
def st():
    if "maxprice" in request.query:
        maxprice = request.query['maxprice']
    else:
        maxprice = 55000
    #DBcon.delete_table('Results')
    for parser_name in PARSER_LIST:
        t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))    	
        t.daemon = True
        t.start()
    redirect("/")
    

# start parse (ONE parser)
@get("/parsers/special_parse")
def spp():
    #maxprice = int(request.query.maxprice)
    parser_name = request.query.parser_name
    if parser_name == 'vk':
        maxprice = 100
    else:
        maxprice = 15000
    t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))
    t.daemon = True
    t.start()
    redirect('/')


#---------------------------------RESULTS & STATUSES------------------------------


# clear tables with parsing results
@get("/results/clearAll")
def clear():
    DBcon.delete_table('Results')
    DBcon.delete_table('Snimu')
    #db.format()
    redirect('/')


# get parsed results
@get("/results/giveMeResults/<parser>")
def res(parser):
    return Parse(parser).get_results()


# get stats for a parser
@get("/statuses/giveMeStatus/<parser>")
def return_status(parser):
    #resp.set_header("Cache-Control", 'no-store, no-cache, must-revalidate, max-age=0')
    return Parse(parser).get_status()


# all parsers list
@get("/statuses/plist")
def pl():
    return json.dumps(PARSER_LIST)


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

    # fetch offers
    res = DBcon.fetch(cmnd)
    count = DBcon.fetch(cmnd_count)[0][0]
    print(count)

    res = json.dumps(res)

    if "html" in q:
        if q['html'] == "off":
            return res
        if q['html'] == "count":
            return count
        
    # insert all flats json into JS template
    return open('./html/tableRes.html', 'r', encoding='windows-1251').read().replace('{{{cnt}}}', str(count)).replace('{{{offr}}}', res).encode('windows-1251')


#-----------------------------------VK POSTS API-----------------------------------------


@get("/giveMePosts/<category>")
def posts(category):
    if 'num' in request.query:
        if request.query['num'] != "":
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

@get("/map/geolocate")
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


@get("/map/locvar_storage.js")
def locvar():
    return static_file('/locvar_storage.js', root='.')



#----------------------------------------------DataBASE----------------------------------------------------


# download db
@get("/db/download")
def db():
    return static_file("parseRes.db", root='.', download=True)


# upload db to dropbox
@get("/db/sync")
def snc():
    #try:
    upload_db()
    redirect('/system')
    #except:
     #   alertExc()


#---------------------------------------STATISTICS SERVICE-----------------------------------------


# get stats for a metro station
@get("/stats")
def stats():
    return html("stats")


# retrieve stats from the db
@get("/stats/giveMeStats")
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



#----------------------------------------------STUFF--------------------------------------------

     
# get any image
@get("/pics/<filename>")
def pics(filename):
    return static_file(filename, root='./pics')


# styles
@get("/css/<filename>")
def css(filename):
    return static_file(filename, root='./css')

@get("/ptest")
def t():
    return "testPassed"


#------------------------------------------------------------------------------------------------

# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
