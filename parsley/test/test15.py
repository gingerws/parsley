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

##@package parsley.test.test15
## Test: metadata integrity

import random, subprocess, shutil, traceback, signal, random, threading, datetime

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(
                DefaultRemove(),
                MetadataSynchronizationWithShadow(),
                path="m",
                name="master"),
            SshfsFilesystem(
                TrashRemove(),
                MetadataSynchronization(),
                sshtarget="pino@localhost",
                path=mydir+"s",
                idfile=mydir+"/loginkey",
                port=42921,
                timeout=timedelta(seconds=4),
                options=["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"], name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    runs = 2

    class State:

        def __init__(self):
            self.files = {}
            self.dump = "|DUMP:"

        def populatemachine(self, lm, length):
            flat = random.choice([True, False])
            for fi in range(40):
                b = "" if flat else random.choice([
                    "", "w/", "w/x/", "w/x/y/", "w/x/y/z/"
                ])
                content = "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for x in range(10)])
                number = int(length * 2)
                fnm = b + "f" + lm + str(fi)
                self.files[fnm] = (content, )
                self.dump += "create '" + content + " in " + fnm + ";"
                write2file(lm + "/" + fnm, "x" * number)
                metadata.setfilemetadata(lm + "/" + fnm, "foo", content)

        def updatemachine(self, length):
            upd = []
            for fi in range(20):
                remove = random.choice([True, False])
                mach = random.choice(["m", "s"])
                tok = None
                while tok is None:
                    tok = random.choice(list(self.files.keys()))
                    fulltok = mydir + mach + "/" + tok
                    if tok in upd:
                        tok = None
                    elif not os.path.exists(fulltok):
                        tok = None
                if remove:
                    os.remove(fulltok)
                    self.files[tok] = (None, )
                    self.dump += "deleted " + tok + ";"
                else:
                    content = "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for x in range(10)])
                    self.files[tok] = (content, )
                    rewrite = random.choice([True, False])
                    self.dump += "updated '" + content + " in " + tok + (" with rewrite" if rewrite else " without rewrite") + ";"
                    if rewrite:
                        number = int(length * 2)
                        write2file(mach + "/" + tok, "x" * number)
                    metadata.setfilemetadata(mach + "/" + tok, "foo", content)
                upd += [tok]

        def checkmachine(self, lm):
            for f in self.files:
                (c,) = self.files[f]
                dfn = lm + "/" + f
                if c is None:
                    if os.path.exists(mydir + dfn):
                        self.dump += "was not deleted: " + dfn + ";"
                        return False
                else:
                    fc = metadata.getfilemetadata(dfn, "foo")
                    if fc != c:
                        self.dump += "got " + dfn + ":" + (fc or "None") + ";"
                        return False
            return True

    with TemporarySshFs(mydir) as tempssh:
        with RateLimiter():
            (for10secs, conn_oh) = measure_network()
            with Disturbator(conn_oh, tempssh, mydir):
                for ir in range(runs):
                    state = State()
                    for lm in ["m", "s"]:
                        state.populatemachine(lm, for10secs)
                    for iir in range(3):
                        print("begin pass "+str(iir))
                        succ = False
                        if iir > 0:
                            state.updatemachine(for10secs)
                        while not succ:
                            try:
                                SYNC()
                                succ = True
                            except Exception as e:
                                print(e)
                        good = state.checkmachine("m") and state.checkmachine("s")
                        if not good:
                            verify(False, str(ir + 1) + " failed; " + state.dump)
                            sys.exit(1)
                    verify(True, str(ir + 1) + " passed")
                    RESET()
