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

##@package parsley.test.test4
## Test: symlinks

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(
                TrashRemove(trashdelay=timedelta(seconds=10)),
                path="m",name="master"),
            LocalFilesystem(
                TrashRemove(trashdelay=timedelta(seconds=10)),
                path="s",name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost",name="test",
            interval=timedelta(seconds=0)
    ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("s/d1/f1","f1")
    write2file("m/d1/f2","f2")
    write2file("s/d1/f3","f3")
    link("d1/f1","s/l1")
    link("d1/f2","s/l2")
    link("d1/f3","m/l3")
    link("d1/f4","s/l4")
    link("l3","s/l5")
    link("d1","m/ll1")
    link("d1","m/ll2")
    link("d1/f2","m/ll3")
    link("d1/f1","s/ll3")
    link("d1","m/ll4")
    SYNC()
    verify(readfile("m/d1/f1")=="f1", "f1 on m")
    verify(readfile("m/l1")=="f1", "l1=f1 on m")
    verify(islink("m/l1")=="d1/f1", "l1 links f1 on m")
    verify(readfile("m/d1/f2")=="f2", "f2 on m")
    verify(readfile("m/l2")=="f2", "l2=f2 on m")
    verify(islink("m/l2")=="d1/f2", "l2 links f2 on m")
    verify(readfile("m/d1/f3")=="f3", "f3 on m")
    verify(readfile("m/l3")=="f3", "l3=f3 on m")
    verify(islink("m/l3")=="d1/f3", "l3 links f3 on m")
    verify(readfile("s/d1/f1")=="f1", "f1 on s")
    verify(readfile("s/l1")=="f1", "l1=f1 on s")
    verify(islink("s/l1")=="d1/f1", "l1 links f1 on s")
    verify(readfile("s/d1/f2")=="f2", "f2 on s")
    verify(readfile("s/l2")=="f2", "l2=f2 on s")
    verify(islink("s/l2")=="d1/f2", "l2 links f2 on s")
    verify(readfile("s/d1/f3")=="f3", "f3 on s")
    verify(readfile("s/l3")=="f3", "l3=f3 on s")
    verify(islink("s/l3")=="d1/f3", "l3 links f3 on s")
    verify(islink("m/l5")=="l3", "l5 links l3 on m")
    verify(islink("s/l5")=="l3", "l5 links l3 on s")
    verify(haslogentry("ll3",verb="conflict"), "ll3 has log entry for conflict")
    verify(islink("m/ll3")=="d1/f2", "m ll3")
    verify(islink("s/ll3")=="d1/f1", "s ll3")
    verify(islink("s/ll1")=="d1", "ll1 links d1 on s")
    verify(islink("m/ll1")=="d1", "ll1 links d1 on m")
    deletefile("s/l1")
    deletefile("s/l2")
    deletefile("s/ll1")
    link("d1/f1","m/ll1")
    link("d1/f1","m/ll2")
    link("d1/f2","m/ll4")
    link("d1/f1","s/ll4")
    write2file("s/l2","l2")
    SYNC()
    verify(readfile("m/d1/f3")=="f3", "f3 on m")
    verify(readfile("m/l3")=="f3", "l3=f3 on m")
    verify(islink("m/l3")=="d1/f3", "l3 links f3 on m")
    verify(readfile("s/d1/f3")=="f3", "f3 on s")
    verify(readfile("s/l3")=="f3", "l3=f3 on s")
    verify(islink("s/l3")=="d1/f3", "l3 links f3 on s")
    verify(not exists("m/l1"), "m l1 doesnt exist")
    verify(not exists("s/l1"), "s l1 doesnt exist")
    verify(haslogentry("l2",verb="conflict"), "l2 has log entry for conflict")
    verify(readfile("s/l2")=="l2", "s l2")
    verify(islink("m/l2")=="d1/f2", "m l2")
    verify(islink("s/ll1")=="d1/f1", "ll1 links d1/f1 on s")
    verify(islink("m/ll1")=="d1/f1", "ll1 links d1/f1 on m")
    verify(islink("m/ll1")=="d1/f1", "m ll1")
    verify(islink("m/ll2")=="d1/f1", "m ll2")
    verify(islink("s/ll2")=="d1/f1", "s ll2")
    verify(haslogentry("ll4",verb="conflict"), "ll4 has log entry for conflict")
    verify(islink("m/ll4")=="d1/f2", "m ll4")
    verify(islink("s/ll4")=="d1/f1", "s ll4")

