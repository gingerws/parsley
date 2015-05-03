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

##@package parsley.test.test17
## Test: subsequent trash remove

import random, subprocess, shutil, traceback, signal, random, threading, datetime, time

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)), path="m", name="master"),
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)), path="s", name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0),
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("m/_dummy1", "")
    write2file("s/_dummy2", "")
    write2file("m/file", "X")
    SYNC()
    verify(readfile("m/file") == "X", "m file")
    verify(readfile("s/file") == "X", "s file")
    deletefile("m/file")
    SYNC()
    verify(readtrashedfile("s/file") == "X", "s file trashed")
    time.sleep(11)
    SYNC()
    verify((not fileexiststrashed("m/file")) and (not fileexiststrashed("m/file..0")) and (not fileexists("m/file")),
           "m file removed")
    verify((not fileexiststrashed("s/file")) and (not fileexiststrashed("s/file..0")) and (not fileexists("s/file")),
           "s file removed")
    write2file("m/file", "Y")
    SYNC()
    verify(readfile("m/file") == "Y", "m file")
    verify(readfile("s/file") == "Y", "s file")
    deletefile("m/file")
    SYNC()
    verify(readtrashedfile("s/file") == "Y", "s file trashed")
    time.sleep(11)
    SYNC()
    verify((not fileexiststrashed("m/file")) and (not fileexiststrashed("m/file..0")) and (not fileexists("m/file")),
           "m file removed")
    verify((not fileexiststrashed("s/file")) and (not fileexiststrashed("s/file..0")) and (not fileexists("s/file")),
           "s file removed")
    write2file("m/file", "Z")
    SYNC()
    verify(readfile("m/file") == "Z", "m file")
    verify(readfile("s/file") == "Z", "s file")
    deletefile("m/file")
    SYNC()
    write2file("m/file", "ZZ")
    SYNC()
    deletefile("m/file")
    SYNC()
    verify(readtrashedfile("s/file") + readtrashedfile("s/file..0") == "ZZZ", "s file trashed")
    time.sleep(11)
    SYNC()
    verify((not fileexiststrashed("m/file")) and (not fileexiststrashed("m/file..0")) and (not fileexists("m/file")),
           "m file removed")
    verify((not fileexiststrashed("s/file")) and (not fileexiststrashed("s/file..0")) and (not fileexists("s/file")),
           "s file removed")
