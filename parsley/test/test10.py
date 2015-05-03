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

##@package parsley.test.test10
## Test: version history

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(DefaultRemove(), RevisionTracking(), path="m", name="master"),
            LocalFilesystem(TrashRemove(), path="s", name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("m/a/b/c/x", "x")
    write2file("s/a/b/c/y", "y")
    write2file("m/f1", "1")
    write2file("m/f2", "1")
    write2file("s/f3", "1")
    write2file("s/_dummy", "")  # otherwise the other dir gets empty which is a bad thing for the watchdog
    SYNC()
    write2file("m/a/b/c/x", "X")
    deletefile("s/f1")
    SYNC()
    time.sleep(1)
    write2file("s/a/b/c/y", "Y")
    write2file("s/f1", "2")
    write2file("m/f2", "2")
    SYNC()
    time.sleep(1)
    deletedir("m/a")
    write2file("m/f1", "3")
    deletefile("m/f2")
    deletefile("s/f3")
    SYNC()
    deletefile("m/f1")
    SYNC()
    verify(len(listdir("s")) == 2, "s empty")
    verify(len(listdir("m")) == 2, "m empty")
    for f in [1, 2, 3]:
        p = "m/.parsley.control/content_revisions/f{f}/".format(f=f)
        l = listdir(p)
        t = 4 - f
        verify(len(l) == t, "versions of f" + str(f))
        found = {}
        for kk in [1, 2, 3][:t]:
            found[kk] = False
        l.sort()
        for li, ll in enumerate(l):
            cont = readfile(p + ll)
            try:
                if int(cont) == li + 1:
                    found[li + 1] = True
            except ValueError:
                pass
        for kk in [1, 2, 3][:t]:
            verify(found[kk], str(kk) + " version of f" + str(f))
    for f in ["x", "y"]:
        p = "m/.parsley.control/content_revisions/a/b/c/" + f
        l = listdir(p)
        lo = False
        up = False
        for ll in l:
            t = readfile(p + "/" + ll)
            if t == f: lo = True
            if t == f.upper(): up = True
        verify(lo, f + " lowercase")
        verify(up, f + " uppercase")
        verify(len(l) == 2, "number in a/b/c")
