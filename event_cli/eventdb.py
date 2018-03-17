"""
DB Access Class for events.
"""

import os.path as path
import sqlite3
import time

__version__ = '0.0.1'

# There was no event before this block.
MIN_BLOCK = 556780


class EventDB:

    __slots__ = ("path", "verbose", "last_height", "db", "cursor")

    def __init__(self, db_path='./.data', verbose=0):
        self.verbose = verbose
        self.path = db_path
        self.last_height = MIN_BLOCK
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
        if not self.last_height:
            self.last_height = MIN_BLOCK

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
            self._db_execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_key ON status (key)")
            self._db_commit()
            self._db_commit()
            """
            events are the events themselves: event name, tx timetamp, txid, payload 
            """
            self._db_execute("CREATE TABLE IF NOT EXISTS events (event TEXT, timestamp float, txid TEXT, payload TEXT)")
            self._db_commit()
            self._db_execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_txid ON events (txid)")
            self._db_commit()
            self._db_execute("CREATE INDEX IF NOT EXISTS idx_event ON events (event)")
            self._db_commit()
            """
            owners are the owner logs of all events
            """
            self._db_execute("CREATE TABLE IF NOT EXISTS owners (event TEXT, timestamp float, owner TEXT)")
            self._db_commit()
            self._db_execute("CREATE INDEX IF NOT EXISTS idx_event2 ON owners (event)")
            self._db_commit()
            self._db_execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON owners (timestamp)")
            self._db_commit()
            """
            sources are the allowed sources logs of all events (current owner is duplicated in sources)
            """
            self._db_execute("CREATE TABLE IF NOT EXISTS sources (event TEXT, timestamp float, sources TEXT)")
            self._db_commit()
            self._db_execute("CREATE INDEX IF NOT EXISTS idx_event3 ON sources (event)")
            self._db_commit()
            self._db_execute("CREATE INDEX IF NOT EXISTS idx_timestamp2 ON sources (timestamp)")
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
                print("Error c", e)
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
            except sqlite3.IntegrityError:
                break
            except Exception as e:
                print("Error", e)
                time.sleep(0.1)

    def get_status(self, key):
        self._db_execute_param('select value from status where key=?', (key,))
        res = self.cursor.fetchone()
        if res:
            res = res[0]
        # print(key, res)
        return res

    def set_status(self, key, value):
        if self.verbose:
            print("Set status ", key, "to", value)
        self._db_execute_param('insert or replace into status values (?, ?, ?)', (key, value, time.time()))
        self._db_commit()

    def get_sources(self, event_name):
        """
        :param event_name:
        :return: List of the current valid sources for this event.
        """
        self._db_execute_param('select sources from sources where event=? order by timestamp desc limit 1',
                               (event_name, ))
        res = self.cursor.fetchone()
        if res:
            res = res[0].split(',')
        if self.verbose:
            print("get_sources", event_name, res)
        return res

    def get_follow(self):
        """
        What events to follow?
        :return: List of event_name
        """
        res = self.get_status('follow')
        if res:
            res = res.split(',')
        return res

    def get_rewinded_events(self, following, rewind=10):
        """
        Generator: list of stored events
        :param following: list of events to fetch
        :param rewind: how many old events to fetch from the db
        :return:
        """
        nb = ['?' for _ in following]
        # Use of a temp table to get the last, but order them in ascending order.
        # Allows to do the job on the db side, and fetching the rows one by one in python for the generator.
        self._db_execute_param('select * from (select * from events where event in ('+','.join(nb)+') order by timestamp desc limit ?) temp order by timestamp asc;',
                               tuple(following)+(rewind,))
        # If we only store the followed and not all, we could use like
        # SELECT * FROM mytable LIMIT 10 OFFSET (SELECT COUNT(*) FROM mytable)-10;
        res = self.cursor.fetchone()
        while res:
            res = {"event": res[0], "ts": res[1], "sig": res[2], "data": res[3]}
            yield(res)
            res = self.cursor.fetchone()

    def set_owner(self, event_name, owner, timestamp):
        """
        Records new owner event
        :param event_name:
        :param owner:
        :param timestamp:
        :return:
        """
        try:
            self._db_execute_param('insert into owners values (?, ?, ?)', (event_name, timestamp, owner))
            self._db_commit()
            sources = self.get_sources(event_name)
            if not sources:
                sources = owner
            else:
                if owner not in sources:
                    sources.append(owner)
                # serialize for storage
                sources = ','.join(sources)
            self._db_execute_param('insert into sources values (?, ?, ?)', (event_name, timestamp, sources))
            self._db_commit()
        except Exception as e:
            print(e)

    def save_event(self, event):
        """
        Records a tracked event
        :param event:
        :return:
        """
        self._db_execute_param('insert into events values (?, ?, ?, ?)',
                               (event['event'], event['ts'], event['txid'], event['data']))
        self._db_commit()


if __name__ == "__main__":
    print("I'm a module, can't run!")
