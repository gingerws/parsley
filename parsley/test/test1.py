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

##@package parsley.test.test1
## Test: very basic functionality

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

    write2file("m/d1/d2/f1", "f1")
    write2file("m/d1/d2/f2", "f2")
    write2file("m/d1/f3", "f3a")
    write2file("m/d1/d2/d3/f4", "f4")
    write2file("m/D1/f5", "a")
    write2file("m/d5/d6/f11", "x")
    write2file("m/d5/d7", "x")
    write2file("s/d5/d7/f11", "x")
    write2file("s/d5/d6", "x")
    write2file("s/d1/d2/f6", "f6")
    write2file("m/d8/f20", "x")
    write2file("m/d8/f21", "x")
    write2file("s/d2/f7", "f7")
    time.sleep(2)
    write2file("s/d1/f3", "f3b")
    write2file("s/d1/d2/d4/f8", "f8")
    write2file("s/D1/f5", "b")
    write2file("m/trashcolltest/f2", "f2b")
    SYNC()
    verify(isdir("m/d1"), "m d1 is directory")
    verify(isdir("m/d1/d2"), "m d1/d2 is directory")
    verify(isdir("m/d1/d2/d3"), "m d1/d2/d3 is directory")
    verify(isdir("m/d2"), "m d2 is directory")
    verify(isdir("m/d1/d2/d4"), "m d1/d2/d4 is directory")
    verify(isdir("s/d1"), "s d1 is directory")
    verify(isdir("s/d1/d2"), "s d1/d2 is directory")
    verify(isdir("s/d1/d2/d3"), "s d1/d2/d3 is directory")
    verify(isdir("s/d2"), "s d2 is directory")
    verify(isdir("s/d1/d2/d4"), "s d1/d2/d4 is directory")
    verify(isdir("m/d5/d6"), "m d6 is directory")
    verify(isdir("s/d5/d7"), "s d7 is directory")
    verify(readfile("m/d1/d2/f1") == "f1", "m f1 contains f1")
    verify(readfile("m/d1/d2/f2") == "f2", "m f2 contains f2")
    verify(readfile("m/d1/d2/d3/f4") == "f4", "m f4 contains f4")
    verify(readfile("m/d1/d2/f6") == "f6", "m f6 contains f6")
    verify(readfile("m/d2/f7") == "f7", "m f7 contains f7")
    verify(readfile("m/d1/d2/d4/f8") == "f8", "m f8 contains f8")
    verify(readfile("s/d1/d2/f1") == "f1", "s f1 contains f1")
    verify(readfile("s/d1/d2/f2") == "f2", "s f2 contains f2")
    verify(readfile("s/d1/d2/d3/f4") == "f4", "s f4 contains f4")
    verify(readfile("s/d1/d2/f6") == "f6", "s f6 contains f6")
    verify(readfile("s/d2/f7") == "f7", "s f7 contains f7")
    verify(readfile("s/d1/d2/d4/f8") == "f8", "s f8 contains f8")
    verify(readfile("m/D1/f5") == "a", "m f5 contains a")
    verify(readfile("s/D1/f5") == "b", "s f5 contains b")
    verify(readfile("m/d1/f3") == "f3a", "m f3 contains f3a")
    verify(readfile("s/d1/f3") == "f3b", "s f3 contains f3b")
    verify(readfile("m/d5/d7") == "x", "m d7 contains x")
    verify(readfile("s/d5/d6") == "x", "s d6 contains x")
    verify(haslogentry("d5/d7", verb="conflict"), "d7 has log entry for conflict")
    verify(haslogentry("d5/d6", verb="conflict"), "d6 has log entry for conflict")
    verify(haslogentry("d1/f3", verb="conflict"), "m f3 has log entry for conflict")
    verify(haslogentry("D1/f5", verb="conflict"), "D1 f5 has log entry for conflict")
    write2file("m/d1/d2/f9", "f9")
    write2file("s/d1/d2/fA", "fA")
    write2file("m/d1/d2/d6/f11", "f11")
    write2file("s/d1/d2/d6/f12", "f12")
    deletefile("m/d1/d2/f1")
    deletefile("s/d1/d2/f2")
    deletefile("s/trashcolltest/f2")
    write2file("s/d2/f7", "f7neu")
    time.sleep(2)
    deletefile("m/d2/f7")
    write2file("m/d8/f20", "y")
    write2file("s/d8/f21", "z")
    SYNC()
    verify(readfile("s/d8/f20") == "y", "s f20 contains y")
    verify(readfile("m/d8/f20") == "y", "m f20 contains y")
    verify(readfile("s/d8/f21") == "z", "s f21 contains z")
    verify(readfile("m/d8/f21") == "z", "m f21 contains z")
    verify(readfile("m/d2/f7") == "f7neu", "m f7 contains f7neu")
    verify(readfile("s/d2/f7") == "f7neu", "s f7 contains f7neu")
    verify(haslogentry("d1/d2/f1", verb="trash"), "m f1 has log entry")
    verify(haslogentry("d1/d2/f2", verb="trash"), "m f2 has log entry")
    verify(haslogentry("trashcolltest/f2", verb="trash"), "trashcolltest/f2 has log entry")
    verify(trashed("s/d1/d2/f1") == "f1", "f1 trashed")
    verify(trashed("m/d1/d2/f2") == "f2", "f2 trashed")
    verify(trashed("m/trashcolltest/f2") == "f2b", "trashcolltest/f2 trashed")
    verify(not fileexists("s/d1/d2/f1"), "f1 removed")
    verify(not fileexists("m/d1/d2/f2"), "f2 removed")
    verify(not fileexists("m/trashcolltest/f2"), "trashcolltest/f2 removed")
    verify(readfile("s/d2/f7") == "f7neu", "s f7 contains f7neu")
    verify(readfile("m/d1/d2/f9") == "f9", "m f9 contains f9")
    verify(readfile("s/d1/d2/fA") == "fA", "s fA contains fA")
    verify(readfile("m/d1/d2/d6/f11") == "f11", "m f11 contains f11")
    verify(readfile("s/d1/d2/d6/f12") == "f12", "s f12 contains f12")
    verify(readfile("s/d1/d2/f9") == "f9", "s f9 contains f9")
    verify(readfile("m/d1/d2/fA") == "fA", "m fA contains fA")
    verify(readfile("s/d1/d2/d6/f11") == "f11", "s f11 contains f11")
    verify(readfile("m/d1/d2/d6/f12") == "f12", "m f12 contains f12")
    verify(readfile("m/d1/d2/d3/f4") == "f4", "m f4 contains f4")
    verify(readfile("m/d1/d2/f6") == "f6", "m f6 contains f6")
    verify(readfile("m/d1/d2/d4/f8") == "f8", "m f8 contains f8")
    verify(readfile("s/d1/d2/d3/f4") == "f4", "s f4 contains f4")
    verify(readfile("s/d1/d2/f6") == "f6", "s f6 contains f6")
    verify(readfile("s/d1/d2/d4/f8") == "f8", "s f8 contains f8")
    verify(readfile("m/D1/f5") == "a", "m f5 contains a")
    verify(readfile("s/D1/f5") == "b", "s f5 contains b")
    verify(readfile("m/d1/f3") == "f3a", "m f3 contains f3a")
    verify(readfile("s/d1/f3") == "f3b", "s f3 contains f3b")
    verify(readfile("m/d5/d7") == "x", "m d7 contains x")
    verify(readfile("s/d5/d6") == "x", "s d6 contains x")
    verify(haslogentry("d5/d7", verb="conflict"), "d7 has log entry")
    verify(haslogentry("d5/d6", verb="conflict"), "d6 has log entry")
    verify(haslogentry("d1/f3", verb="conflict"), "m f3 has log entry for conflict")
    time.sleep(5)
    SYNC()
    verify(trashed("s/d1/d2/f1") == "f1", "f1 trashed")
    verify(trashed("m/d1/d2/f2") == "f2", "f2 trashed")
    verify(trashed("m/trashcolltest/f2") == "f2b", "trashcolltest/f2 trashed")
    time.sleep(5)
    SYNC()
    verify((not fileexistspattern("s/d1/d2/f1")) and (trashed("s/d1/d2/f1") is None ), "f1 purged")
    verify((not fileexistspattern("m/d1/d2/f2")) and (trashed("m/d1/d2/f2") is None ), "f2 purged")
    verify((not fileexistspattern("m/trashcolltest/f2")) and (trashed("m/trashcolltest/f2") is None ),
           "trashcolltest/f2 purged")
    verify(haslogentry("d5/d7", verb="conflict"), "d7 has log entry for conflict")
    verify(haslogentry("d5/d6", verb="conflict"), "d6 has log entry for conflict")
    verify(haslogentry("d1/f3", verb="conflict"), "m f3 has log entry for conflict")
    verify(haslogentry("D1/f5", verb="conflict"), "D1 f5 has log entry for conflict")
    verify(readfile("m/D1/f5") == "a", "m f5 contains a")
    verify(readfile("s/D1/f5") == "b", "s f5 contains b")
    verify(readfile("m/d1/f3") == "f3a", "m f3 contains f3a")
    verify(readfile("s/d1/f3") == "f3b", "s f3 contains f3b")
    verify(readfile("m/d5/d7") == "x", "m d7 contains x")
    verify(readfile("s/d5/d6") == "x", "s d6 contains x")

