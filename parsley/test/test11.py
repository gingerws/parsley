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

##@package parsley.test.test11
## Test: integrity

import random

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(DefaultRemove(), path="m", name="master"),
            LocalFilesystem(TrashRemove(), path="_s", name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0),
            preparations=[SshfsMountPreparation(src="pino@localhost:" + mydir + "s",
                                                tries=2, timeout=timedelta(seconds=4),
                                                tgt="_s", idfile=mydir+"/loginkey", port=42921,
                                                options=["-o", "StrictHostKeyChecking=no", "-o",
                                                         "UserKnownHostsFile=/dev/null"])]
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    runs = 3

    class State:

        def __init__(self):
            self.files = {}
            self.dump = "|DUMP:"

        def populatemachine(self, lm, length):
            flat = random.choice([True, False])
            for fi in range(random.choice([4, 7, 11])):
                b = "" if flat else random.choice([
                    "", "w/", "w/x/", "w/x/y/", "w/x/y/z/"
                ])
                content = "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for x in range(10)])
                number = int(length * 102.4 / len(content))
                fnm = b + "f" + lm + str(fi)
                self.files[fnm] = (content, number)
                self.dump += "create '" + content + "'*" + str(number) + " in " + fnm + ";"
                write2file(lm + "/" + fnm, content * number)

        def updatemachine(self, length):
            upd = []
            for fi in range(5):
                remove = random.choice([True, False])
                mach = random.choice(["m", "s"])
                tok = None
                while tok == None:
                    tok = random.choice(list(self.files.keys()))
                    fulltok = mydir + mach + "/" + tok
                    if tok in upd:
                        tok = None
                    elif not os.path.exists(fulltok):
                        tok = None
                if remove:
                    os.remove(fulltok)
                    self.files[tok] = (None, -1)
                    self.dump += "deleted " + tok + ";"
                else:
                    content = "".join([random.choice("abcdefghijklmnopqrstuvwxyz") for x in range(10)])
                    number = int(length * 102.4 / len(content))
                    self.files[tok] = (content, number)
                    self.dump += "updated '" + content + "'*" + str(number) + " in " + tok + ";"
                    write2file(mach + "/" + tok, content * number)
                upd += [tok]

        def checkmachine(self, lm):
            for f in self.files:
                (c, n) = self.files[f]
                dfn = lm + "/" + f
                if n == -1:
                    if os.path.exists(mydir + dfn):
                        self.dump += "was not deleted: " + dfn + ";"
                        return False
                else:
                    with open(mydir + dfn, "r") as fil:
                        fc = "\n".join(fil.readlines())[:-1]
                    if fc != c * n:
                        self.dump += "got " + dfn + ":" + fc[0:10] + " in " + str(len(fc)) + "byte;"
                        return False
            return True

    with TemporarySshFs(mydir) as tempssh:
        with RateLimiter():
            (for10secs, conn_oh) = measure_network()
            with Disturbator(conn_oh, tempssh, mydir):
                os.mkdir(mydir + "_s")
                for ir in range(runs):
                    state = State()
                    for lm in ["m", "s"]:
                        state.populatemachine(lm, for10secs)
                    for iir in range(4):
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
                            verify(False, str(ir+1) + " failed; " + state.dump)
                            sys.exit(1)
                    verify(True, str(ir + 1) + " passed")
                    RESET()
                    os.mkdir(mydir + "_s")
