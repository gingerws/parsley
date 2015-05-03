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

##@package parsley.test.test12
## Test: sshfs native

import random, subprocess, shutil, traceback, signal, random, threading, datetime

if "syncs" in globals():
    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(TrashRemove(), path="m", name="master"),
            SshfsFilesystem(TrashRemove(), sshtarget="pino@localhost", path=mydir+"/s", idfile=mydir+"/loginkey",
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

    with TemporarySshFs(mydir):
        write2file("m/d1/d2/f1", "f1")
        write2file("m/d1/d2/f2", "f2")
        write2file("m/d1/f3", "f3")
        write2file("s/d5/d7/f4", "f4")
        write2file("s/d5/d6/f5", "f5")
        write2file("s/d1/d2/f6", "f6")

        SYNC()

        verify(readfile("m/d1/d2/f1") == "f1", "m f1 contains f1")
        verify(readfile("m/d1/d2/f2") == "f2", "m f2 contains f2")
        verify(readfile("m/d1/f3") == "f3", "m f3 contains f3")
        verify(readfile("s/d1/d2/f1") == "f1", "s f1 contains f1")
        verify(readfile("s/d1/d2/f2") == "f2", "s f2 contains f2")
        verify(readfile("s/d1/f3") == "f3", "s f3 contains f3")
        verify(readfile("m/d5/d7/f4") == "f4", "m f4 contains f4")
        verify(readfile("m/d5/d6/f5") == "f5", "m f5 contains f5")
        verify(readfile("m/d1/d2/f6") == "f6", "m f6 contains f6")
        verify(readfile("s/d5/d7/f4") == "f4", "s f4 contains f4")
        verify(readfile("s/d5/d6/f5") == "f5", "s f5 contains f5")
        verify(readfile("s/d1/d2/f6") == "f6", "s f6 contains f6")


