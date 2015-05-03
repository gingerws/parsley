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

##@package parsley.test.test2
## Test: MoveSink/MoveSattelite pair

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(
                TrashRemove(trashdelay=timedelta(seconds=10)),
                PullAndPurgeSyncSink(),
                path="m", name="master"),
            LocalFilesystem(
                TrashRemove(trashdelay=timedelta(seconds=10)),
                PullAndPurgeSyncSource(),
                path="s", name="slave"),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("s/d1/d2/f1", "f1")
    write2file("s/d1/d2/f2", "f2")
    write2file("m/d1/f3", "f3")
    SYNC()
    verify(readfile("m/d1/d2/f1") == "f1", "m f1 contains f1")
    verify(readfile("m/d1/d2/f2") == "f2", "m f2 contains f2")
    verify(readfile("m/d1/f3") == "f3", "m f3 contains f3")
    verify(len(filesindir("s/")) == 0, "slave empty")
    write2file("s/d1/d2/f2", "f2b")
    write2file("s/d1/f4", "f4")
    write2file("m/d1/f5", "f5")
    SYNC()
    verify(readfile("m/d1/d2/f1") == "f1", "m f1 contains f1")
    verify(readfile("m/d1/d2/f2.1") == "f2", "m f2 contains f2")
    verify(readfile("m/d1/f3") == "f3", "m f3 contains f3")
    verify(readfile("m/d1/f4") == "f4", "m f4 contains f4")
    verify(readfile("m/d1/f5") == "f5", "m f5 contains f5")
    verify(readfile("m/d1/d2/f2") == "f2b", "m f2.1 contains f1b")
    verify(len(filesindir("s/")) == 0, "slave empty")


