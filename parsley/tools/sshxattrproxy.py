#!/usr/bin/env python3

# Copyright (C) 2014-2015, Josef Hahn
#
# This file is part of parsley.
#
# parsley is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# parsley is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with parsley.  If not, see <http://www.gnu.org/licenses/>.

##@package parsley.tools.sshxattrproxy
## SSH remote proxy for exchange of file metadata.

import base64
import os

import sys
import xattr
import _thread
import threading
import datetime
import time

## This program is not directly used in the process of the parsley engine but is copied to a remote system
## and controlled via an ssh session as a proxy for doing some tasks on this remote system, which cannot
## be done via an sshfs mount.
class Mainloop:

    def __init__(self):
        self.rootdir = None
        self.lastalive = datetime.datetime.now()
        self.lastalivelock = threading.Lock()
        self.running = True

    def _watchdog(self):
        while True:
            time.sleep(60)
            with self.lastalivelock:
                if (datetime.datetime.now() - self.lastalive).total_seconds() >= 60 * 60 * 2:
                    os._exit(1)

    def run(self):
        sys.stdout.write("SSHXATTRPROXY_READY\n")
        sys.stdout.flush()
        _thread.start_new_thread(self._watchdog, ())
        while True:
            rawreq = sys.stdin.readline()
            req = eval(base64.b64decode(rawreq).decode())
            doraise = False
            try:
                res = repr(self.processrequest(req))
            except Exception as e:
                res = repr(e)
                doraise = True
            rawres = base64.b64encode(res.encode(errors='backslashreplace')).decode()
            if doraise:
                rawres += " RAISE"
            sys.stdout.write(rawres + " DONE\n")
            sys.stdout.flush()
            with self.lastalivelock:
                self.lastalive = datetime.datetime.now()
            if not self.running:
                os._exit(0)

    def processrequest(self, req):
        cmd = req[0]
        if cmd == "init":
            self.rootdir = req[1]
            return "ACK"
        elif cmd == "listxa":
            fpath = self.rootdir + "/" + req[1]
            res = xattr.list(fpath)
            return [x.decode("utf-8") for x in res]
        elif cmd == "getxa":
            fpath = self.rootdir + "/" + req[1]
            key = req[2]
            return xattr.get(fpath, key).decode("utf-8")
        elif cmd == "setxa":
            fpath = self.rootdir + "/" + req[1]
            key = req[2]
            value = req[3]
            xattr.set(fpath, key, value)
            return None
        elif cmd == "unsetxa":
            fpath = self.rootdir + "/" + req[1]
            key = req[2]
            xattr.remove(fpath, key)
            return None
        elif cmd == "shutdown":
            self.running = False
        else:
            raise Exception("command not understood: "+cmd)

Mainloop().run()