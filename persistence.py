import sqlite3
import configparser
from abc import ABC, abstractmethod


class Persistence(ABC):

    @abstractmethod
    def get_messages(self, id):
        pass

    @abstractmethod
    def put_message(self, question, result, url):
        pass

def get_persistence_layer():
    config = configparser.ConfigParser()
    config.read('config.ini')
    persistence = config['DEFAULT']['persistence']

    if persistence == "sqlite":
        return PersistenceSQLite()
    else:
        return None

class PersistenceSQLite(Persistence):
    def __init__(self):
        self.con = sqlite3.connect("results.db")
        self.cur = self.con.cursor()

    def get_messages(self, id=None):
        if id:
            try:
                intid = int(id)
                res = self.cur.execute("SELECT rowid, claim, result, url FROM results where rowid = {}".format(intid))
            except:
                print("Not a valid ID")
                return []
        else:
            res = self.cur.execute("SELECT rowid, claim, result, url FROM results ORDER BY rowid DESC LIMIT 20")

        messages = []
        for row in res.fetchall():
            messages.append({'id': row[0],
                             'claim': row[1],
                             'result': row[2],
                             'url': row[3]})

        return messages

    def put_message(self, question, result, url):
        data = ({'claim': question, 'result': result, 'url': url})
        self.cur.execute("INSERT INTO results VALUES (:claim, :result, :url)", data)
        self.con.commit()
        res = self.cur.execute("SELECT last_insert_rowid()")
        id = res.fetchall()[0][0]

        return id
