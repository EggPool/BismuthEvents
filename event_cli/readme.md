# A very basic command line client for Bismuth Event

Follows an event feed and displays the last messages.

Needs a node from 2019-03-17 or later.

# requirements

WIP

* python 3.5 +  
* sqlite3 should be the only "exotic" required module.  
* needs a node to connect to, with access rights to the newest 'API_' features.

# Config

* `event_cli.default.conf` is the default cofig file, that comes with the release. It's *noy* to be modified
* create a `event-cli.conf` file and override your custom settings there if needed. 

# How to use

Run `python3 event_cli.py --watch` 

Run naked for usage:

# Command line

usage: event_cli.py [-h] [-v] [--follow FOLLOW] [--unfollow UNFOLLOW] [--list] [--watch]

optional arguments:  
  * -h, --help           show this help message and exit  
  * -v, --verbose        Force verbose mode.  
  * --follow FOLLOW      Add an event to follow list  
  * --unfollow UNFOLLOW  Remove an event from follow list  
  * --list               Display current follow list  
  * --watch              Tail the events stream  
