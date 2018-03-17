#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple event client for Bismuth

@EggPool

"""

import sys
import os
import time
import argparse

# custom modules
sys.path.append('../modules')
import eventconfig
from simpleeventclient import SimpleEvent


__version__ = "0.0.2"


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


if __name__ == "__main__":
    parser = MyParser(description='Bismuth Event client from EggPool.Net')
    #parser = argparse.ArgumentParser(description='Bismuth Event client from EggPool.Net')
    parser.add_argument("-v","--verbose", action="count", default = False,  help='Force verbose mode.')
    # TODO
    #parser.add_argument("--rescan", action="count", default = 0, help='Force a rescan of the ledger')
    parser.add_argument("--follow", type=str,  default = None, help='Add an event to follow list')
    parser.add_argument("--unfollow", type=str,  default = None, help='Remove an event from follow list')
    parser.add_argument("--list", action="count", default = 0, help='Display current follow list')
    parser.add_argument("--watch", action="count", default = 0, help='Tail the events stream')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    event_config = eventconfig.Get()
    # add our current code version
    event_config.version = __version__
    # Force verbose
    if args.verbose:
        event_config.verbose = True
    try:
        simple_event = SimpleEvent(event_config)
        if args.follow:
            simple_event.follow(args.follow)
        if args.unfollow:
            simple_event.unfollow(args.unfollow)
        if args.list:
            print("Following: {}.".format(",".join(simple_event.following)))
            pass
        if args.watch:
            simple_event.watch()
            while True:
                time.sleep(10)
    except Exception as e:
        # At launch, it's ok to close if the node is not available.
        # TODO: once started, disconnects and reconnects have to be taken care of seemlessly.
        print("Unable to connect to node :", e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        sys.exit()


