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

import datetime
import time
import os
import signal
import subprocess
import threading
from parsley.preparations.mountpreparation import MountPreparation
from parsley.preparations import Preparation
from parsley.tools.common import call
from parsley.tools.networking import translate_parsley_portforwarding

## Mounts remote filesystems with sshfs.
class SshfsMountPreparation(Preparation):
    def __init__(self, *, src, tgt, idfile=None, password=None, port=22,
                 options=None, timeout=datetime.timedelta(seconds=10),
                 **kwa):
        Preparation.__init__(self, **kwa)
        self.src = src
        self.tgt = os.path.abspath(tgt)
        self.idfile = idfile
        self.password = password
        self.port = port
        self.options = options if options else []
        self.timeout = timeout

    @staticmethod
    def translateToAlternativeEndpoint(src, port, runtime):
        u = ""
        pa = ""
        i = src.find("@")
        if i > -1:
            u = src[:i + 1]
            src = src[i + 1:]
        i = src.rfind(":")
        if i > -1:
            pa = src[i:]
            src = src[:i]
        (m, p) = translate_parsley_portforwarding(src, port, runtime)
        return u + m + pa, p

    def enable(self, runtime):
        ret = None

        def timeoutthread(p, secs):
            nonlocal ret
            for i in range(int(secs * 10)):
                time.sleep(0.1)
                if ret is not None:
                    break
            try:
                p.send_signal(signal.SIGINT)
            except Exception:
                pass

        try:
            if not os.path.exists(self.tgt):
                os.makedirs(self.tgt)
            opts = []
            port = 22
            if self.port:
                port = self.port
            (real_src, real_port) = SshfsMountPreparation.translateToAlternativeEndpoint(self.src, port, runtime)
            opts += ["-p", str(real_port)]
            opts += [real_src, self.tgt]
            if self.idfile:
                opts += ["-o", "IdentityFile=" + self.idfile]
            for option in self.options:
                opts.append(option)
            if self.password:
                opts += ["-o", "password_stdin"]
            sacm = str(max(int(self.timeout.total_seconds() / 2), 2))
            opts += ["-o", "ServerAliveCountMax=" + sacm, "-o", "ServerAliveInterval=2"]
            pwd = (self.password + "\n").encode("utf-8") if self.password else ""
            MountPreparation._checkmountpointempty(self.tgt)
            p = subprocess.Popen(["sshfs"] + opts,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            threading.Thread(target=timeoutthread, args=(p,
                                                         self.timeout.total_seconds() * 3)).start()
            if self.password:
                time.sleep(2)
            rr = p.communicate(pwd)
            r = rr[0].decode("utf-8") + "; " + rr[1].decode("utf-8")
            p.stdin.close()
            ret = p.wait()
            if ret != 0:
                raise Exception(self.src + " not mounted: " + r)
            time.sleep(0.5)
        finally:
            if ret is None:
                ret = -1  # stop the thread under all circumstances

    def disable(self, runtime):
        try:
            # noinspection PySimplifyBooleanCheck
            if self.getstate(runtime) is False:
                return
        except Exception:
            pass
        call("sync")
        call("sync")
        time.sleep(0.5)
        (ret, r) = call("fusermount", "-u", self.tgt)
        if ret != 0:
            time.sleep(1)
            raise Exception(self.src + " not unmounted: " + r)
        time.sleep(0.5)

    def getstate(self, runtime):
        (ret, r) = call(["mount"])
        if ret != 0:
            raise Exception("list mounts error: " + r)
        return r.find(" " + self.tgt + " ") > -1


