#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A -very- stripped down Bismuth node.py client for the event client.
@EggPool

"""

# Generic modules
import threading
import time

# Bismuth specific modules
from rpcconnections import Connection
from eventdb import EventDB
"""
Note: connections.py is legacy. Will be replaced by a "command_handler" class. WIP, see protobuf code.
"""

__version__ = '0.0.1'

# Interface versioning
API_VERSION = '0.1b'


class SimpleEvent:
    """
    Connects to a node.py via socket.
    """
    
    __slots__ = ("config", "connection", "event_db", "stop_event", "last_height", "watchdog_thread")
    
    def __init__(self, config):
        self.config = config
        self.stop_event = threading.Event()
        # TODO: read from db or local temp file
        self.last_height = 556780 # no event before
        # TODO: raise error if missing critical info like bismuth node/path
        node_ip, node_port = self.config.bismuthnode.split(":")
        self.connection = Connection((node_ip, int(node_port)), verbose=config.verbose)
        self.event_db = EventDB(verbose=config.verbose)
        self.watchdog_thread = threading.Thread(target=self._watchdog)
        self.watchdog_thread.daemon = True
        self.watchdog_thread.start()

    def _poll(self):
        """
        Will ask the node for the new blocks/tx since last known state and run through filters
        :return:
        """
        if self.config.verbose:
            print("Polling", self.last_height)
        blocks = self.connection.command("api_getblockswhereoflike", [self.last_height, 'event:'])
        # devrait renvoyer dernier block, même si rien, pour savoir où raccrocher.
        if len(blocks):
            self.last_height = blocks[-1]
            #  TODO: persistently save last_height to self.eventdb
            self.event_db.set_status('last_height', self.last_height)
        del blocks[-1]
        if len(blocks):
            for tx in blocks:
                if self.config.verbose:
                    print(tx)
                """
                [(556890, 1521133449.92, 'da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e', 'da8a39cc9d880cd55c324afc2f9596c64fac05b8d41b3c9b6c481b4e', 0, 
                'Ztb+fCyWUjgAw5Ly22UmwYto1iX6lgelc72RU8cslUIX8zfcb6PSJtjUcwQ5wBxXFy0IWXe7YBZlppFmqvxrkRNiwDTX+BDWahqwS2x2M7myQwU42IK6U9eLm8TO9pE0d0n/RbhZVVajV8w3snR+UKj5VTaChvUf2Rdi9AaL0RIIfQ0EBGjoXA19r5wuS9fDrq4CuLEVVc1s03MMjld0tiFOqTHeHeT4f9jL2RNz2Tk+hgVxHuBaroG2QWGU7OgDfFk58dmnIbUSdOCSoNqsnc66c0T2Gfxy9MxYB33tpAYYnIJz1Kd85lNRXjElOMmQsoRzeCJuwwCk/Q3Oc/9uQxJpKUjO3u5x0WuDqWyhurv6U57aF0aaEx1fC/wWdVAUH/Pqx+O+xFPd14wrKzO3l/dkFCRPv/iSldL3qLp//WVWItDAYmRXCB/a7X+8G2Mu9PB6anZjF5/2SSpay/dp09F1EXOnuEWayYYCkmy7YwF7oqNYxxcy/RLK0wqjNISwkcudD+lEVIkRnNpTvg9+j5asrL6bXNAz4hHvXGXqDRObZPLz6e04kuAAUdE7d/vNXn4a8m5UgX2dHxDwr6qJt13nQXZKtd7irc1t+Jix/f5z/p6/4woQGgEJBEUn8axeuAIJqaWUgyWv59ZUgW2SL1vm2BBImvmapQ6btkcZWR8=', 
                'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFwbjBoM3BiZkZMcUJzdy92ZGw3ZAp5Z0xrNWFpUW1tZlhaNzRQTE56eVQwb3FTNWJORUZhSXIzdVNwUjk4WG84Rm5lOGhjbkxvVFB0Y1lhWndUWDJECjRjakxhYm9HaWxkY1l4Vkt3ajNRQlh1Vk9kODh6OWN4TXFsNGt3U3I0bTI2Y1dWQ2VsMXdzZjdlbkRzZ0xpbW8KMFpOaUhocTAyNVI0R1FMSi9HRzhCcmFjQTFlL1g2TkhuZStaWGtjU2dYOTVDNlF6YXU2UEVuczZldVZQLzlOaApWNGlxempEOEI4MmE2T3RHYkxqdjkvVE9UK3hpN29kTHZyMUVUejhEUC9qM2RmMlRTY2YwTURYUTZwR05PV0NoClV2SlVIVkpVamd1cVdBQS94Q2pObWpBSk4wN2NSamRsRzZReUxzZi8xNk9XeUVmKzIxR0VkendmYXRPV2syN20KV1VrMnNNakxLN3JoYmZNc1B4ZDJrd3FZa21sS1d2akNzY25sdXpNNnVwTHJlNWdieVo0b1dVMklxVXczTzYzYwp4cjg3R1VLL2x1RzNLZTNhYitheWJFbTVaWG5pcmtMZ3NXakhCMFlUdS9xdE9HaWhiYXY0WEpPK290cXZ1SlhPClJ4OFpGdWg0TFh3N3hNdytlY1p3Y3dpeDlUTEErSVhTNjJkcFdYWE80WFdXLzliYUw3bGUvVXhwbTFXaEpQRDUKM1RmemJBSy8wNE9MT3dxc2RjdFBTbUp1cHRiYVVwTTNIeEtGbFBQemFIZ2NQRW55VC9HRHJwUUJxdXFJKzVkTApabzBXZ2ZXMEtzRTFiVXdWNTJUOEhnblBDck9EbnczeUhFVVdyTjNMZUszZjFkNnQvM200Ujc4TmJUQzJlT0lsCnpvNjlvRTFyMzJnWUp6dndwcXJwNGYwQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==', 
                'fefe470a131e0b5171cc5a24778cc3fa9d085cc06a77ae19bcf9fbb0', 0.01013, 0, 0, 'event:reg:Egg')]
                """
                # TODO some things
        # at launch, if we are not at max height, then run in loop.

    def _ping_if_needed(self):
        """
        Sends a ping if 29 sec or more passed since last activity, to keep connection open
        :return:
        """
        if self.connection.last_activity < time.time()-29:
            #print("Sending Ping")
            ret = self.connection.command("api_ping")
            #print(ret)

    def _watchdog(self):
        """
        called in a thread to send ping and poll the node if needed.
        :return:
        """
        # Give it some time to start and do things
        time.sleep(2)
        while not self.stop_event.is_set():
            if self.config.poll:
                self._poll()
            self._ping_if_needed()
            # 10 sec is a good compromise.
            time.sleep(10)

    def getinfo(self, *args, **kwargs):
        """
        Returns a dict with the node info
        Could take a param like verbosity of returned info later.
        """
        try:
            # TODO: connected check and reconnect if needed. But will be handled by the connection layer. Don't bother here.
            # Moreover, it's not necessary to keep a connection open all the time. Not all commands need one, so it just need to connect on demand if it is not.
            info = self.connection.command("statusjson")
            """
            info = {"version":self.config.version, "protocolversion":"mainnet0016", "walletversion":data[7], "testnet":False, # config data
                    "balance":10.00, "blocks":data[5], "timeoffset":0, "connections":data[1], "difficulty":109.65, # live status
                    "errors":""} # to keep bitcoind compatibility
            """
            # add extra info
            info["version"] = self.config.version
            info["errors"] = ""
        except Exception as e:
            info = {"version":self.config.version, "error":str(e)}
        return info



if __name__ == "__main__":
    print("I'm a module, can't run!")