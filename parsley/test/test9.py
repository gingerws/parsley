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

##@package parsley.test.test9
## Test: direct transitive sync

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(DefaultRemove(), path="m", name="master"),
            LocalFilesystem(TrashRemove(trashdelay=timedelta(days=9)), path="sa", name="slave_a"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhorst-a", name="test",
            interval=timedelta(seconds=20)
        ))

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(DefaultRemove(), path="m", name="master"),
            LocalFilesystem(TrashRemove(trashdelay=timedelta(days=9)), path="sb", name="slave_b"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhorst-b", name="test",
            interval=timedelta(seconds=20)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("m/f1", "f1")
    write2file("sa/f2", "f2")
    write2file("sb/f3", "f3")
    write2file("m/_dummy1", "")  # otherwise the other dir gets empty which is a bad thing for the watchdog
    write2file("sa/_dummy2", "")  # otherwise the other dir gets empty which is a bad thing for the watchdog
    write2file("sb/_dummy3", "")  # otherwise the other dir gets empty which is a bad thing for the watchdog
    SYNC()
    verify(readfile("m/f1") == "f1", "m f1")
    verify(readfile("m/f2") == "f2", "m f2")
    verify(readfile("m/f3") == "f3", "m f3")
    verify(readfile("sa/f1") == "f1", "sa f1")
    verify(readfile("sa/f2") == "f2", "sa f2")
    verify(readfile("sa/f3") == "f3", "sa f3")
    verify(readfile("sb/f1") == "f1", "sb f1")
    verify(readfile("sb/f2") == "f2", "sb f2")
    verify(readfile("sb/f3") == "f3", "sb f3")
    deletefile("m/f1")
    deletefile("sa/f2")
    deletefile("sb/f3")
    time.sleep(30)
    SYNC()
    for a in ["m", "sa", "sb"]:
        for b in ["f1", "f2", "f3"]:
            verify(not exists(a + "/" + b), a + "/" + b + " not exists")
