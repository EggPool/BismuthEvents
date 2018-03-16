"""
DB Access Class for events.
"""

import os.path as path
import sqlite3
import time

__version__ = '0.0.1'


class EventDB:

    __slots__ = ("path", "verbose", "last_height", "db", "cursor")

    def __init__(self, path='./.data', verbose=0):
        self.verbose = verbose
        self.path = path
        # no event before
        self.last_height = 556780
        self.db = None
        self.cursor = None
        # Init
        self._read_db()

    def _read_db(self):
        """
        read current state at launch
        :return:
        """
        if not path.exists(self.path+'/events.db'):
            self._create_db()
        else:
            self.db = sqlite3.connect(self.path+'/events.db', timeout=1)
            self.db.text_factory = str
            self.cursor = self.db.cursor()
        self.last_height = self.get_status('last_height')
        if  not self.last_height:
            self.last_height = 556780

    def _create_db(self):
        """
        Creates initial DB if it doesn't exists yet
        :return:
        """
        if self.verbose:
            print("Initializing DB")
        try:
            self.db = sqlite3.connect(self.path+'/events.db', timeout=1)
            self.db.text_factory = str
            self.cursor = self.db.cursor()
            """
            Status stores all params. current height, followed events  
            """
            # TODO: add indexes
            self._db_execute("CREATE TABLE IF NOT EXISTS status (key TEXT, value TEXT, timestamp float)")
            self._db_commit()
            """
            events are the events themselves: event name, tx timetamp, txid, payload 
            """
            self._db_execute("CREATE TABLE IF NOT EXISTS events (event TEXT, timestamp float, txid TEXT, payload TEXT)")
            self._db_commit()
            """
            owners are the owner logs of all events
            """
            self._db_execute("CREATE TABLE IF NOT EXISTS owners (event TEXT, timestamp float, owner TEXT)")
            self._db_commit()
            """
            sources are the allowed sources logs of all events (current owner is duplicated in sources)
            """
            self._db_execute("CREATE TABLE IF NOT EXISTS sources (event TEXT, timestamp float, sources TEXT)")
            self._db_commit()
            if self.verbose:
                print("Recreated events db")
        except Exception as e:
            print("Error", e)

    def _db_commit(self):
        """Secure commit for slow nodes"""
        while True:
            try:
                self.db.commit()
                break
            except Exception as e:
                print("Error", e)
                time.sleep(0.1)

    def _db_execute(self, query):
        """Secure execute for slow nodes"""
        while True:
            try:
                self.cursor.execute(query)
                break
            except Exception as e:
                print("Error", e)
                time.sleep(0.1)

    def _db_execute_param(self, query, param):
        """Secure execute w/ param for slow nodes"""
        while True:
            try:
                self.cursor.execute(query, param)
                break
            except Exception as e:
                print("Error", e)
                time.sleep(0.1)

    def get_status(self, key):
        self._db_execute_param('select value from status where key=?', (key,))
        res = self.cursor.fetchone()
        #print(key, res)
        return res

    def set_status(self, key, value):
        print("Should set status ", key, "to", value)
        """self._db_execute_param('select value from status where key=?', (key,))
        res = self.cursor.fetchone()
        #print(key, res)
        return res
        """

if __name__ == "__main__":
    print("I'm a module, can't run!")