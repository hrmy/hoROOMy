# This Python file uses the following encoding: utf-8

import json
import requests
from database import DataBase, DBcon
from time import gmtime, strftime
from driveAPI import BackuppedFile
from botAPI import alertExc, alertBot


# when we start app.py
# sync db
BackuppedFile('parseRes.db').sync()


#------------------------------------------------------

try:
    DBcon.format()
except:
    print("db already formatted")
print("!!!db created!!!")
#------------------------------------------------------


# for phone numbers, not to use lambda
def evolve(a):
    if a is not None:
        a = a.replace("+7", "").replace(" ","").replace("-","").replace("(","").replace(")","")
        if len(a) == 11:
            return a[1:]
    else:
        a = '---'
    return a
    

# for optimizating work of all parsers
class Parse:
    name = ""
    db = None


    def __init__ (self, name):
        self.name = name
        #self.status_file = "./statuses/" + name + ".txt"
        #self.results_file = "./results/" + name + ".json"
        self.db = DataBase('parseRes.db')   # self db connection to enable multithreading
                                            # (MAYBE NO NEED FOR IT IN MULTIPROCESSING?)


    """def save_results(self, results):
        res = json.dumps(results)
        f = open(self.results_file, 'a', encoding='utf-8')
        f.write(res)
        f.close()"""


    # for statistics abouth the number of links processed
    def write_status(self, status):

        cmnd = "DELETE FROM Statuses WHERE name = '%s';" % self.name
        self.db.query(cmnd)

        cmnd = "INSERT INTO Statuses VALUES ('%s', '%s')" % (self.name, str(status))
        self.db.query(cmnd)
        

    # last updated on...
    def add_date(self):
        data = "last updated on: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        self.write_status(data)


    def get_results(self):
        cmnd = "SELECT * FROM Results WHERE fromwhere = '%s';" % self.name
        return json.dumps(self.db.fetch(cmnd), ensure_ascii=False)

    def get_status(self):
        try:
            cmnd = "SELECT status FROM Statuses WHERE name = '%s';" % self.name
            return self.db.fetch(cmnd)[0][0]
        except:
            return ''

    
    # appending to db (like to #a list)
    def append(self, data, useHash=False):       # working with db

        def get_id(data):
            unique_id = str(data['cost']) + str(data['room_num']) + str(data['area']) + str(data['loc'])
            return unique_id

        if data['adr'] == None:
            print("""-----REMOVED FOR NO ADDR GIVEN -----""")
            return 0

        
        # get coordinates if we know adress
        def get_loc(adr):
            api_adr = adr.replace(' ', '+')
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % api_adr
            loc = requests.get(url).text
            loc = json.loads(loc)
            print("!!!GET_LOC USED!!!")
            loc = loc['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]['pos']
            loc = list(loc.split(" "))
            loc = loc[1] + "," + loc[0]
            return loc


        # get adress if we know coordinates
        def get_adr(loc):
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % loc
            adr = requests.get(url).text
            adr = json.loads(adr)
            print("!!!GET_ADR USED!!!")
            return adr['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        

    #  SET CHECK IF THE FLAT ALREADY EXISTS   !!!!!!!!!!!!!!!!!!!!!


    # getting loc and adr
        if ("adr" in data and "loc" not in data) or (data['loc'] == []) or (data['loc'] == ""):
            try:
                data["loc"] = get_loc(data["adr"])
            except:
                data['loc'] = "YANDEXLOCERR"
                print('YANDEXLOCERR')


        elif ("loc" in data and "adr" not in data) or (data['adr'] == ""):
            try:
                data["adr"] = get_adr(data["loc"])
            except:
                data['adr'] = 'YANDEXADRERR'
                print("YANDEXADRERR")


        # unique id for the descr
        if useHash: 
            hsh = hash(data['descr'])
        else:
            hsh = get_id(data)

        # delete duplicates
        cmnd = "DELETE FROM Results WHERE hash='%s';" % hsh
        self.db.query(cmnd)
        
        # forming db command
        cmnd = """
INSERT INTO Results VALUES (
'%s',
%s,
%s,
%s,
'%s',
'%s',
'%s',
'%s',
'%s',
'%s',
'%s',
'%s',
"%s",
'%s',
'%s'
);
""" % (hsh, data['cost'], data['room_num'], data['area'], evolve(data['contacts']['phone']), data['date'], 'NULL', json.dumps(data['pics'], ensure_ascii=False), json.dumps(data['contacts'], ensure_ascii=False), data['descr'], data['adr'], json.dumps(data['metro'], ensure_ascii=False), data['url'], json.dumps(data['loc']), self.name)
        #print(cmnd)
        self.db.query(cmnd)
        print("\n\n-----ONE MORE WITH "+self.name+"-----\n\n")


    def append_snimu(self, data):

        hsh = hash(data['descr'].encode('utf-8')) # unique id

        cmnd = "DELETE FROM Snimu WHERE hash='%s';" % hsh   # remove duplicates
        self.db.query(cmnd)
        
        #print(str(data))
        cmnd = """
    INSERT INTO Snimu VALUES (
    '%s',
    %s,
    %s,
    '%s',
    '%s',
    '%s',
    '%s',
    '%s',
    '%s'
    );
    """ % (hsh, data['cost'], data['room_num'], json.dumps(data['metro'], ensure_ascii=False), evolve(data['contacts']['phone']), json.dumps(data['contacts'], ensure_ascii=False), data['url'], json.dumps(data['pics'], ensure_ascii=False), data['descr'])
        self.db.query(cmnd)
        print("\n\n-----ONE RENTER WITH "+self.name+"-----\n\n")

    def __del__(self):
        del self.db

















    
