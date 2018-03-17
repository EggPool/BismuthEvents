#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple GUI event client for Bismuth

"""

import sys
import os
#import time
#import argparse

# custom modules
sys.path.append('../modules')
import eventconfig
from simpleeventclient import SimpleEvent


__version__ = "0.0.1"


if __name__ == "__main__":
    event_config = eventconfig.Get(base_name='event_tk')
    # add our current code version
    event_config.version = __version__
    try:
        simple_event = SimpleEvent(event_config)
        print(simple_event.following)
        """
        simple_event.watch()
        while True:
            time.sleep(10)
        """
    except Exception as e:
        # At launch, it's ok to close if the node is not available.
        print("Unable to connect to node :", e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        sys.exit()
