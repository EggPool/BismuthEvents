#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Bismuth node.py client for event management.
@EggPool
Needs >= ??? Node Version.
"""

# Generic modules
import threading
import time
import datetime
import sys
import os
import base64

# Bismuth specific modules
from rpcconnections import Connection
from eventdb import EventDB
"""
Note: connections.py is legacy. Will be replaced by a "command_handler" class. WIP, see protobuf code.
"""

__version__ = '0.0.2'


class SimpleEvent:
    """
    Connects to a node.py via socket.
    """
    
    __slots__ = ("config", "connection", "event_db", "event_db_watch", "stop_event", "last_height", "watchdog_thread",
                 "watching_event", "following")
    
    def __init__(self, config):
        try:
            self.config = config
            self.stop_event = threading.Event()
            self.watching_event = threading.Event()
            node_ip, node_port = self.config.bismuthnode.split(":")
            self.connection = Connection((node_ip, int(node_port)), verbose=config.verbose)
            self.event_db = EventDB(verbose=config.verbose, db_path=config.db_path)
            self.last_height = self.event_db.get_status('last_height')  # no event before
            if not self.last_height:
                self.last_height = 556780  # no event before
            else:
                self.last_height = int(self.last_height)
            self.event_db_watch = None
            self.watchdog_thread = threading.Thread(target=self._watchdog)
            self.watchdog_thread.daemon = True
            self.watchdog_thread.start()
            self.following = []
            if self.config.follow:
                self.following = self.config.follow.split(',')
            db_follow = self.event_db.get_follow()
            if db_follow:
                self.following.extend(db_follow)
            if self.config.verbose:
                print("Follow {}".format(",".join(self.following)))
        except Exception as e:
            print("Error init SimpleEvent :", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

    def follow(self, follow):
        """
        Add event(s) to follow to the db
        :param follow:a string with event_names to follow, comma separated
        :return:
        """
        follow = follow.split(',')
        self.following.extend(follow)
        db_follow = self.event_db.get_follow()
        if db_follow:
            db_follow.extend(follow)
        else:
            db_follow = follow
        self.event_db.set_status('follow', ','.join(db_follow))

    def unfollow(self, unfollow):
        """
        Remove event(s) to follow from the db
        :param follow:a string with event_names to follow, comma separated
        :return:
        """
        unfollow = unfollow.split(',')
        self.following = [x for x in self.following if x not in unfollow]
        db_follow = self.event_db.get_follow()
        if db_follow:
            db_follow = [x for x in db_follow if x not in unfollow]
            self.event_db.set_status('follow', ','.join(db_follow))

    def watch(self, rewind=10):
        """
        Poll new blocks and display new events
        :param rewind:Display last rewind events from db
        :return: True if is watching
        """
        if self.watching_event.is_set():
            if self.config.verbose:
                print("Already watching")
            return True
        for event in self.event_db.get_rewinded_events(self.following, 10):
            self.display_event(event)
        self.watching_event.set()
        if self.config.verbose:
            print("Watching On")
        return True

    def unwatch(self):
        """
        Stop polling
        :return:
        """
        self.watching_event.clear()
        if self.config.verbose:
            print("Watching Off")

    def _poll(self):
        """
        Will ask the node for the new blocks/tx since last known state and run through filters
        :return:
        """
        if not self.watching_event.is_set():
            return False
        if self.config.verbose:
            print("Polling", self.last_height)
        blocks = self.connection.command("api_getblockswhereoflike", [self.last_height, 'event:'])
        # Last item of the list is the last processed block ,even if no tx was in there.
        if len(blocks):
            self.last_height = blocks[-1][0]
            #  Save last_height to db
            self.event_db_watch.set_status('last_height', self.last_height)
            del blocks[-1]
        if len(blocks):
            for tx in blocks:
                if self.config.verbose:
                    print(tx)
                """
                [556890, 1521133449.92, 'da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e', 'da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e', 0,
                 0       1              2                                                            3                                                         4 
                'Ztb+fCyWUjgAw5Ly22UmwYto1iX6lgelc72RU8cslUIX8zfcb6PSJtjUcwQ5wBxXFy0IWXe7YBZlppFmqvxrkRNiwDTX+BDWahqwS2x2M7myQwU42IK6U9eLm8TO9pE0d0n/RbhZVVajV8w3snR+UKj5VTaChvUf2Rdi9AaL0RIIfQ0EBGjoXA19r5wuS9fDrq4CuLEVVc1s03MMjld0tiFOqTHeHeT4f9jL2RNz2Tk+hgVxHuBaroG2QWGU7OgDfFk58dmnIbUSdOCSoNqsnc66c0T2Gfxy9MxYB33tpAYYnIJz1Kd85lNRXjElOMmQsoRzeCJuwwCk/Q3Oc/9uQxJpKUjO3u5x0WuDqWyhurv6U57aF0aaEx1fC/wWdVAUH/Pqx+O+xFPd14wrKzO3l/dkFCRPv/iSldL3qLp//WVWItDAYmRXCB/a7X+8G2Mu9PB6anZjF5/2SSpay/dp09F1EXOnuEWayYYCkmy7YwF7oqNYxxcy/RLK0wqjNISwkcudD+lEVIkRnNpTvg9+j5asrL6bXNAz4hHvXGXqDRObZPLz6e04kuAAUdE7d/vNXn4a8m5UgX2dHxDwr6qJt13nQXZKtd7irc1t+Jix/f5z/p6/4woQGgEJBEUn8axeuAIJqaWUgyWv59ZUgW2SL1vm2BBImvmapQ6btkcZWR8=',
                5 
                'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFwbjBoM3BiZkZMcUJzdy92ZGw3ZAp5Z0xrNWFpUW1tZlhaNzRQTE56eVQwb3FTNWJORUZhSXIzdVNwUjk4WG84Rm5lOGhjbkxvVFB0Y1lhWndUWDJECjRjakxhYm9HaWxkY1l4Vkt3ajNRQlh1Vk9kODh6OWN4TXFsNGt3U3I0bTI2Y1dWQ2VsMXdzZjdlbkRzZ0xpbW8KMFpOaUhocTAyNVI0R1FMSi9HRzhCcmFjQTFlL1g2TkhuZStaWGtjU2dYOTVDNlF6YXU2UEVuczZldVZQLzlOaApWNGlxempEOEI4MmE2T3RHYkxqdjkvVE9UK3hpN29kTHZyMUVUejhEUC9qM2RmMlRTY2YwTURYUTZwR05PV0NoClV2SlVIVkpVamd1cVdBQS94Q2pObWpBSk4wN2NSamRsRzZReUxzZi8xNk9XeUVmKzIxR0VkendmYXRPV2syN20KV1VrMnNNakxLN3JoYmZNc1B4ZDJrd3FZa21sS1d2akNzY25sdXpNNnVwTHJlNWdieVo0b1dVMklxVXczTzYzYwp4cjg3R1VLL2x1RzNLZTNhYitheWJFbTVaWG5pcmtMZ3NXakhCMFlUdS9xdE9HaWhiYXY0WEpPK290cXZ1SlhPClJ4OFpGdWg0TFh3N3hNdytlY1p3Y3dpeDlUTEErSVhTNjJkcFdYWE80WFdXLzliYUw3bGUvVXhwbTFXaEpQRDUKM1RmemJBSy8wNE9MT3dxc2RjdFBTbUp1cHRiYVVwTTNIeEtGbFBQemFIZ2NQRW55VC9HRHJwUUJxdXFJKzVkTApabzBXZ2ZXMEtzRTFiVXdWNTJUOEhnblBDck9EbnczeUhFVVdyTjNMZUszZjFkNnQvM200Ujc4TmJUQzJlT0lsCnpvNjlvRTFyMzJnWUp6dndwcXJwNGYwQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==',
                6 
                'fefe470a131e0b5171cc5a24778cc3fa9d085cc06a77ae19bcf9fbb0', 0.01013, 0, 0, 'event:reg:Egg']
                7                                                            8       9 10  11
                """
                self._digest_event(tx)
        # at launch, if we are not at max height, then run in loop.

    def display_event(self, json_event):
        """
        Print out the event (will evolve)
        :param json_event:
        :return:
        """
        clear = base64.b85decode(json_event['data'].encode('utf-8')).decode("utf-8")
        date_time = datetime.datetime.fromtimestamp(json_event['ts']).strftime('%Y-%m-%d %H:%M:%S')
        # TODO: will depend on the type of the event.
        print("{} > {} : {}".format(date_time, json_event['event'], clear))

    def _digest_event(self, tx):
        """
        Validates, processes and saves the event
        :param tx:
        :return:
        """
        event = self._validate_event(tx)
        if self.config.verbose:
            print(event)
        if event:
            if event['cmd'] == 'msg':
                # save message in db if followed or saving all
                # TODO: deal with save all
                if event['event'] in self.following:
                    self.display_event(event)
                    self.event_db_watch.save_event(event)

    def _validate_event(self, tx):
        """
        Tests the event and return a structured version of the valid events, or None
        :return:
        """
        try:
            # First Step, formal validity of the tx data
            if tx[11][:6] != 'event:':
                raise ValueError('Not an Event data')
            if tx[4] > 0:
                raise ValueError('Event amount has to be null')
            if tx[2] > tx[3]:
                raise ValueError('Address and recipient must be the same')
            if tx[9] > 0:
                raise ValueError('Reward has to be null')
            if tx[10] > 0:
                raise ValueError('Keep has to be equal to 0')
            if tx[11][9] != ':':
                raise ValueError('Event format error.')
            sender = tx[2]  # for clarity sake
            timestamp = tx[1]
            txid = tx[5][:56]
            # TODO: check signature, use a key module.
            # right address?
            # signature ok?
            # Second Step, rights checking. We get the events in chronological order, so
            # Rollbacks may play havoc with rights. TODO: reindex on demand?
            temp = tx[11].split(':')
            if len(temp) == 4:
                _, command, event_name, data = temp
            elif len(temp) == 3:
                _, command, event_name = temp
                data = None
            else:
                raise ValueError('Event format error 2.')
            if command not in ['reg', 'msg', 'xfr', 'add', 'del', 'dsc', 'icn', 'typ']:
                raise ValueError('Unknown event command.')
            if len(event_name) < 3:
                raise ValueError('Minimum Event name len is 3 chars.')
            sources = self.event_db_watch.get_sources(event_name)
            # Registration management
            if command == 'reg':
                if sources:
                    raise ValueError('Invalid duplicate registration')
                # register:
                self.event_db_watch.set_owner(event_name, sender, timestamp)  # Will also define as source
                sources = [sender]
            else:
                if not sources:
                    raise ValueError('Unregistered event.')
            # Rights management
            if sender not in sources:
                raise ValueError('Unauthorized source')
            # TODO: Here we handle the rest of the rights commands
            # Here the message part
            if command == 'msg':
                pass
            return {'cmd': command, 'event': event_name, 'data': data, 'txid': txid, 'ts': timestamp}
        except Exception as e:
            print("Non valid Event", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return None

    def _ping_if_needed(self):
        """
        Sends a ping if 29 sec or more passed since last activity, to keep connection open
        :return:
        """
        if self.connection.last_activity < time.time() - 29:
            self.connection.command('api_ping')

    def _watchdog(self):
        """
        called in a thread to send ping and poll the node if needed.
        :return:
        """
        # Give it some time to start and do things
        time.sleep(2)
        # a db object local to this thread
        self.event_db_watch = EventDB(verbose=self.config.verbose, db_path=self.config.db_path)
        while not self.stop_event.is_set():
            self._poll()
            self._ping_if_needed()
            # 10 sec is a good compromise.
            time.sleep(10)

    def getinfo(self):
        """
        Returns a dict with the node info
        """
        try:
            info = self.connection.command("statusjson")
            """
            info = {"version":self.config.version, "protocolversion":"mainnet0016", "walletversion":data[7], 
                    "testnet":False, # config data
                    "balance":10.00, "blocks":data[5], "timeoffset":0, "connections":data[1], "difficulty":109.65, 
                    "errors":""} # to keep bitcoind compatibility
            """
            # add extra info
            info["version"] = self.config.version
            info["errors"] = ""
        except Exception as e:
            info = {"version": self.config.version, "error": str(e)}
        return info


if __name__ == "__main__":
    print("I'm a module, can't run!")
