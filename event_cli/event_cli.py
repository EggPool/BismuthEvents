#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple event client for Bismuth

@EggPool

"""

import sys
import time

# custom modules
import eventconfig
from simpleeventclient import SimpleEvent



__version__ = "0.0.1"


if __name__ == "__main__":

    event_config = eventconfig.Get()
    # add our current code version
    event_config.version = __version__

    # Temp testing
    event_config.poll = True

    try:
        node = SimpleEvent(event_config)
    except Exception as e:
        # At launch, it's ok to close if the node is not available.
        # TODO: once started, disconnects and reconnects have to be taken care of seemlessly.
        print("Unable to connect to node :", e)
        sys.exit()

    while True:
        time.sleep(10)
        

