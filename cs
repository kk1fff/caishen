#!/usr/bin/env python3

from csbook import CSBookBuilder

from cmd_add  import AddCommand
from cmd_view import ViewCommand
from cmd_rm   import RemoveCommand
from cmd_edit import EditCommand

import os
import sys

###

class Config:
    def __init__(self):
        pass
    def storagePath(self):
        return os.path.expanduser('~/cs')

if __name__ == "__main__":
    config = Config()
    csbook = CSBookBuilder(config)
    cmds = {
        "add":  AddCommand,
        "view": ViewCommand,
        "rm":   RemoveCommand,
        "edit": EditCommand
    }
    params = sys.argv
    cmd = params[1]
    if cmd in cmds:
        cmds[cmd](csbook).run(params[2:])
    else:
        raise Exception("Command not found")
