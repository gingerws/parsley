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

##@package parsley.test.test7
## Test: slight variation of directory removal

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(DefaultRemove(), path="m", name="master"),
            LocalFilesystem(DefaultRemove(), path="s", name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("s/d1/d2/d3/d4/d5/f1", "f1")
    write2file("s/e1/e2/e3/e4/e5/f2", "f2")
    write2file("m/_dummy", "")
    SYNC()
    time.sleep(1)
    verify(readfile("s/d1/d2/d3/d4/d5/f1") == "f1", "s f1")
    verify(readfile("m/e1/e2/e3/e4/e5/f2") == "f2", "m f2")
    write2file("s/d1/d2/f3", "f3")
    write2file("m/e1/e2/f4", "f4")
    deletefile("s/d1/d2/d3/d4/d5/f1")
    deletefile("s/e1/e2/e3/e4/e5/f2")
    deletedir("s/d1/d2/d3/d4/d5/")
    deletedir("s/d1/d2/d3/d4")
    deletedir("s/d1/d2/d3")
    deletedir("s/e1/e2/e3/e4/e5/")
    deletedir("s/e1/e2/e3/e4/")
    deletedir("s/e1/e2/e3/")
    deletedir("s/e1/e2/")
    deletedir("s/e1/")
    SYNC()
    verify(not isdir("m/d1/d2/d3/"), "removed m d3")
    verify(readfile("m/e1/e2/f4") == "f4", "m f4")
    verify(readfile("m/d1/d2/f3") == "f3", "m f3")
    verify(readfile("s/e1/e2/f4") == "f4", "s f4")
    verify(readfile("s/d1/d2/f3") == "f3", "s f3")

