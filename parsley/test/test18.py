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

##@package parsley.test.test18
## Test: no local file removals after remote ssh killed

import random, subprocess, shutil, traceback, signal, random, threading, datetime

if "syncs" in globals():

    from parsley.sync.infs.aspect import Aspect
    from parsley.sync.infs.syncmachine import SyncHooks

    class SleepWhileBeginning(Aspect):
        def __init__(self):
            Aspect.__init__(self)
        def hook(self, machine, isglobal, fss):
            for fs in fss:
                def _beginupdatedir(_fs):
                    def _x(path, runtime):
                        if path == "":
                            if os.path.exists("/var/tmp/_parsley_ctrl_die_in_beginning"):
                                os.unlink("/var/tmp/_parsley_ctrl_die_in_beginning")
                                time.sleep(3)
                    return _x
                machine.addhook(fs, SyncHooks.onbeginupdatedir, 60001, _beginupdatedir(fs))

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(
                DefaultRemove(),
                MetadataSynchronizationWithShadow(),
                path="m",
                name="master"),
            SshfsFilesystem(
                TrashRemove(),
                MetadataSynchronization(),
                SleepWhileBeginning(),
                sshtarget="pino@localhost",
                path=mydir+"s",
                idfile=mydir+"/loginkey",
                port=42921,
                timeout=timedelta(seconds=4),
                options=["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"], name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    with TemporarySshFs(mydir) as tempssh:

        try:
            os.unlink("/var/tmp/_parsley_ctrl_die_in_beginning")
        except IOError: pass

        def wait_and_kill_connection():
            with open("/var/tmp/_parsley_ctrl_die_in_beginning", "w") as f:
                pass
            while os.path.exists("/var/tmp/_parsley_ctrl_die_in_beginning"):
                pass
            dis = Disturbator(0, tempssh, mydir)
            dis.d_killmounter()

        write2file("s/_dummy", "")
        write2file("m/a", "a")

        SYNC()

        write2file("m/b", "b")

        threading.Thread(target=wait_and_kill_connection).start()

        try:
            SYNC()
        except Exception: pass

        verify(readfile("m/a") == "a", "m a")
        verify(readfile("s/a") == "a", "s a")
        verify(readfile("m/b") == "b", "m b")
        verify(not fileexists("s/b"), "s b")

        SYNC()

        verify(readfile("m/a") == "a", "m a")
        verify(readfile("s/a") == "a", "s a")
        verify(readfile("m/b") == "b", "m b")
        verify(readfile("s/b") == "b", "s b")
