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

##@package parsley.test.test5
## Test: filenames with non-ascii characters

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)), path="m", name="master"),
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)), path="s", name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("s/d1/fäöü", "f1")
    write2file("m/f", "f")
    SYNC()
    verify(readfile("m/d1/fäöü") == "f1", "m fäöü umlaut filename")
