"""
Config file manager.
"""

import os.path as path


__version__ = '0.0.1'


class Get:
    
    # "param_name":["type"] or "param_name"=["type","property_name"]
    vars = {"bismuthnode": ["str"], "loglevel": ["str"], "verbose": ["int"], "registrar": ["str"], "follow": ["str"]}
 
    def __init__(self):
        self.verbose = 0
        self.bismuthnode = "127.0.0.1"
        self.registrar = 'any'
        self.read()
 
    def load_file(self, filename):
        #print("Loading", filename)
        for line in open(filename):
            if '=' in line:
                left, right = map(str.strip, line.rstrip("\n").split("="))
                if left not in self.vars:
                    # Warn for unknown param?
                    continue
                params = self.vars[left]
                if params[0] == "int":
                    right = int(right)
                elif params[0] == "list":
                    right = [item.strip() for item in right.split(",")]
                else:
                    # treat as "str"
                    pass 
                if len(params) > 1:
                    # deal with properties that do not match the config name.
                    left = params[1]
                setattr(self, left, right)
                    
    def read(self):
        # first of all, load from default config so we have all needed params
        self.load_file("event_cli.default.conf")
        # then override with optional custom config
        if path.exists("event_cli.conf"):
            self.load_file("event_cli.conf")
        # TODO: raise error if missing critical info like bismuth node
        # Better : raise in the client class, where we need it.
        if self.verbose:
            print(self.__dict__)           


if __name__ == "__main__":
    print("I'm a module, can't run!")
