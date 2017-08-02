import sqlite3


class DataBase:
    name = ''

    _db_connection = None
    _db_cur = None

    def __init__(self, name):
        self.name = name
        self._db_connection = sqlite3.connect(self.name)
        self._db_cur = self._db_connection.cursor()

    def query(self, query):
        self._db_cur.execute(query)
        self._db_connection.commit()
        return

    def fetch(self, query):
        return self._db_cur.execute(query).fetchall()

    def save(self):
        self._db_connection.commit()

    def __del__(self):
        #self._db_connection.commit()
        self._db_connection.close()

    def delete_table(self, table):
        self.query('DELETE FROM %s;' % table)
        self.query('VACUUM;')

    def format(self):
        # places - places of interest
        cmnd_list = []
        cmnd_list.append("""
CREATE TABLE Results (
hash TEXT,
cost INTEGER,
room_num INTEGER,
area INTEGER,
phone TEXT,
date TEXT,
places TEXT,
pics TEXT,
contacts TEXT,
descr TEXT,
adr TEXT,
metro TEXT,
prooflink TEXT,
loc TEXT,
fromwhere TEXT
);
""")

        cmnd_list.append("""
CREATE TABLE Statuses (
name TEXT,
status TEXT
);
""")

        cmnd_list.append("""
CREATE TABLE Snimu (
hash TEXT,
cost INTEGER,
room_num INTEGER,
metro TEXT,
phone TEXT,
contacts TEXT,
prooflink TEXT,
pics TEXT,
descr TEXT
);
""")

        cmnd_list.append("CREATE TABLE alerts (format_dic TEXT);")


        for cmnd in cmnd_list:
            self.query(cmnd)


DBcon = DataBase('parseRes.db')     # global database connection


if __name__ == "__main__":
 #   for name in ["realEstate", "kvartirant", "rentooki", "bezPosrednikov", "sdamsnimu", "sdatsnyat", "rentm", "novoselie", "vkfeed"]:
  #      DataBase('parseRes.db').query("insert into Statuses values ('%s', '4 links processed')" % name)
    #DataBase('parseRes.db').format()
    #DataBase('parseRes.db').query("""insert into alerts values ('''%s''')""" % '''{"version": "0.0.9.130", "added": "---", "othertext": ""}''')
    cmnd = """SELECT avg(cost) from results where metro like '%%ВДНХ%%';
"""
    print(DataBase('parseRes.db').fetch(cmnd))
    




        
