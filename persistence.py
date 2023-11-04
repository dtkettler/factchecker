import sqlite3
from google.cloud import firestore
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
    elif persistence == "firestore":
        return PersistenceFirestore()
    else:
        return None

class PersistenceSQLite(Persistence):
    def __init__(self):
        self.con = sqlite3.connect("results.db", check_same_thread=False)
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

class PersistenceFirestore(Persistence):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')
        project = config['DEFAULT']['firestore_project']

        self.db = firestore.Client(project=project)

    def get_messages(self, id=None):
        if id:
            doc_ref = self.db.collection("results").document(id)
            doc = doc_ref.get()
            if doc.exists:
                result = doc.to_dict()
                result["id"] = doc.id
                results = [result]
            else:
                print("Not a valid ID")
                return []

        else:
            docs = self.db.collection("results").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).stream()
            #docs = self.db.collection("results").limit(20).stream()

            results = []
            for doc in docs:
                result = doc.to_dict()
                result["id"] = doc.id
                results.append(result)

        return results

    def put_message(self, question, result, url):
        data = ({'claim': question, 'result': result, 'url': url, "timestamp": firestore.SERVER_TIMESTAMP})

        update_time, ref = self.db.collection("results").add(data)
        id = ref.id

        return id
