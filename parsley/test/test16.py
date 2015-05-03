#!/usr/bin/python3
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

##@package parsley.test.test16
## Test: dirty copy detection

import random, subprocess, shutil, traceback, signal, random, threading, datetime, time

if "syncs" in globals():
    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(TrashRemove(), path="m", name="master"),
            SshfsFilesystem(TrashRemove(), sshtarget="pino@localhost", path=mydir + "s", idfile=mydir + "/loginkey",
                port=42921,
                options=["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"], name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0),
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    runs = 3

    class ChangerThread(threading.Thread):
        def __init__(self, root, filename, filesize, interval, lst):
            threading.Thread.__init__(self)
            self.root = root
            self.filename = filename
            self.filesize = filesize
            self.content = None
            self.interval = interval
            self.started = datetime.datetime.now()
            self.running = True
            self.deleteafter = filename == lst[0]
            self.lst = lst  # noo, we don't lock it here :-p
            write2file(root + "/" + filename, "")  # we must create it in main thread
            self.daemon = True
            self.start()

        def run(self):
            while datetime.datetime.now() - self.started <= self.interval:
                til = self.interval - (datetime.datetime.now() - self.started)
                writeto = datetime.datetime.now() + datetime.timedelta(seconds=
                                                                       min(random.randint(1, 10), til.total_seconds()))
                while datetime.datetime.now() - self.started <= self.interval and datetime.datetime.now() < writeto:
                    self.content = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                    write2file(self.root + "/" + self.filename, self.content * self.filesize)
                time.sleep(min(random.randint(1, 10), til.total_seconds()))
            if self.deleteafter:
                time.sleep(random.randint(0, 10))
                self.lst.remove(self.filename)
                deletefile(self.root + "/" + self.filename)
            self.running = False

    with TemporarySshFs(mydir) as tempssh:
        with RateLimiter():
            (for10secs, conn_oh) = measure_network()
            with Disturbator(conn_oh, tempssh, mydir):
                passed = 0
                for ir in range(runs):
                    filesize = int(for10secs * 1024 / random.choice([2, 4, 6, 8, 10, 15, 100, 10000])) + 1
                    waittimes = random.randint(0, int(2 * conn_oh + 120))
                    s1, s2 = random.choice([("m", "s"), ("s", "m")])
                    write2file(s1 + "/_dummy", "")
                    th = {}
                    l = ["a", "b", "c", "d", "e", "f", "g"]
                    for ii in range(3):
                        for c in l:
                            th[c] = ChangerThread(s2, c, filesize, datetime.timedelta(seconds=waittimes), l)
                        waiting = True
                        while waiting:
                            if waiting:
                                try:
                                    SYNC()
                                except Exception:
                                    pass
                            waiting = len([1 for x in l if th[x].running]) > 1
                        succ = False
                        while not succ:
                            try:
                                SYNC()
                                succ = True
                            except Exception:
                                pass
                        good = True
                        for ms in ["m", "s"]:
                            good = good and (len(listdir(ms)) == len(l) + 2)  # +2 for .parsley.control and _dummy
                        for c in l:
                            for ms in ["m", "s"]:
                                good = good and (readfile(ms + "/" + c) == th[c].content * filesize)
                        if good:
                            passed += 1
                        verify(good, str(passed) + "/" + str(ir * 3 + ii + 1) + " ran good")
                        if not good:
                            sys.exit(1)
                    RESET()
