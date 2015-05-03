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

##@package parsley.test.test3
## Test: react on io errors

if "syncs" in globals():
    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)),path="m",name="master"),
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)),path="s",name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0),
            preparations=[MountPreparation(src=mydir+"part",tgt=mydir+"m",
            opts=["-o","loop"],)]
    ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    os.makedirs(mydir+"s")
    os.makedirs(mydir+"m")
    subprocess.call(["dd","if=/dev/zero","of="+mydir+"part","bs=4096","count=1000"])
    subprocess.call(["dd","if=/dev/zero","of="+mydir+"s/file","bs=4096","count=1250"])
    subprocess.call(["mkfs.ext3","-F",mydir+"part"])
    subprocess.call(["sudo","mount","-o","loop",mydir+"part",mydir+"m"])
    time.sleep(1)
    subprocess.call(["sudo","chmod","-R", "777",mydir+"m"])
    time.sleep(1)
    subprocess.call(["sudo","umount",mydir+"m"])
    time.sleep(2)
    try:
        SYNC()
    except Exception:pass
    subprocess.call(["sudo","mount","-o","loop",mydir+"part",mydir+"m"])
    verify(trashed("m/_parsley_currenttransfer.1",onlybool=True),"crashed filetransfer deleted")
    verify(readfile("m/file")=="", "file not on m")
    time.sleep(2)
    subprocess.call(["sudo","umount",mydir+"m"])
    time.sleep(2)
    deletefile("s/file")
    try:
        SYNC()
    except Exception:pass
    subprocess.call(["sudo","mount","-o","loop",mydir+"part",mydir+"m"])
    verify(not trashed("m/_parsley_currenttransfer.1",onlybool=True),"crashed filetransfer purged")
    verify(readfile("m/file")=="", "file not on m")
    write2file("s/file","file")
    time.sleep(2)
    subprocess.call(["sudo","umount",mydir+"m"])
    time.sleep(2)
    try:
        SYNC()
    except Exception:pass
    subprocess.call(["sudo","mount","-o","loop",mydir+"part",mydir+"m"])
    verify(readfile("m/file")=="file", "file on m")
    time.sleep(2)
    subprocess.call(["sudo","umount",mydir+"m"])

