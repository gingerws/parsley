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

import base64
import os
import subprocess
import threading
import _thread
import shutil
import datetime
import time
from parsley.logger.severity import Severity
from parsley.preparations.sshfsmountpreparation import SshfsMountPreparation
from parsley.sync.infs.filesystem.local import LocalFilesystem
try:
    import fcntl
except Exception:
    pass


class SshfsFilesystem(LocalFilesystem):
    def __str__(self):
        return "[ssh port:{port} {path}]".format(port=self.port, path=self.rootpath)

    def __init__(self, *aspects, name, sshtarget, path, idfile=None, password=None, port=22,
                 timeout=datetime.timedelta(seconds=10), options=None):
        LocalFilesystem.__init__(self, *aspects, name=name, path=None)  # we set the path later on
        self.sshtarget = sshtarget
        self.targetpath = path
        self.idfile = idfile
        self.password = password
        self.port = port
        self.timeout = timeout
        self.options = options if options else []
        self.sshxattrproxy = None
        self._sshpreparationadded = False

    def initialize(self, infssync, runtime):
        r_target, r_port = SshfsMountPreparation.translateToAlternativeEndpoint(self.sshtarget, self.port, runtime)
        self.sshtarget = r_target
        self.port = r_port
        self.sshpath = self.sshtarget + ":" + self.targetpath
        mountdir = runtime.mydir + "/mounts/" + infssync.fullname
        if not os.path.isdir(mountdir):
            os.makedirs(mountdir)
        self.rootpath = mountdir
        self.sshxattrproxy = None
        if not self._sshpreparationadded:
            sshmountpreparation = SshfsMountPreparation(src=self.sshpath, timeout=self.timeout,
                                                        tgt=mountdir, idfile=self.idfile, port=self.port,
                                                        options=self.options, password=self.password)
            infssync.preparations.append(sshmountpreparation)
            self._sshpreparationadded = True

    def shutdown(self, infssync, runtime):
        if self.sshxattrproxy:
            self.sshxattrproxy.shutdown()
            runtime.log(subject="Spent {secs} seconds in ssh remote proxy.".format(
                secs=self.sshxattrproxy._benchmark.total_seconds()), severity=Severity.BENCHMARK)

    class _SshXattrProxy:

        def _waitanswer(self, endstring, additionaltimeout=0):
            self._ready = False
            self._quark = ""
            self._stopreadywaitthread = False

            def readywaitthread():
                self._quark = ""
                self._finished = False
                while not self._finished and not self._stopreadywaitthread:
                    t = self.sout.read()
                    if t:
                        self._quark += t.decode()
                    self._finished = self._quark.endswith(endstring + "\n")
                    if not self._finished:
                        time.sleep(0.002)
                with self.readywaitlock:
                    self._ready = True
                    self.readywaitcondition.notify_all()

            _thread.start_new_thread(readywaitthread, ())
            timeout = additionaltimeout * 2 + 20  # some extra seconds :)
            with self.readywaitlock:
                while (not self._ready) and (timeout > 0) and (self.sshproc.poll() is None):
                    self.readywaitcondition.wait(0.5)
                    timeout -= 1
            if self.sshproc.poll() is not None:
                raise Exception("ssh xattr remote proxy terminated unexpectedly. received: " + self._quark)
            if not self._ready:
                raise Exception("timeout in communication with the remote ssh xattr proxy. received so far: " +
                                self._quark)
            return self._quark

        def __init__(self, sshfs):
            self.sshfs = sshfs
            self._benchmark = datetime.timedelta()
            proxyfilename = __file__
            _relproxyfilename = "/tools/sshxattrproxy.py"
            while not os.path.isfile(proxyfilename + _relproxyfilename) and proxyfilename != os.path.dirname(proxyfilename):
                proxyfilename = os.path.dirname(proxyfilename)
            proxyfilename += _relproxyfilename
            shutil.copyfile(proxyfilename, self.sshfs.rootpath + "/.parsley.control/sshxattrproxy.py")
            os.chmod(self.sshfs.rootpath + "/.parsley.control/sshxattrproxy.py", 0o755)
            self.sshproc = subprocess.Popen(["ssh", self.sshfs.sshtarget, "-p", str(self.sshfs.port), "-i",
                                            self.sshfs.idfile] + self.sshfs.options +
                                            [self.sshfs.targetpath + "/.parsley.control/sshxattrproxy.py"],
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.sin = self.sshproc.stdin
            self.sout = self.sshproc.stdout
            fcntl.fcntl(self.sout, fcntl.F_SETFL, fcntl.fcntl(self.sout, fcntl.F_GETFL) | os.O_NONBLOCK)
            self.readywaitlock = threading.Lock()
            self.readywaitcondition = threading.Condition(self.readywaitlock)
            self._waitanswer(endstring="SSHXATTRPROXY_READY", additionaltimeout=self.sshfs.timeout.total_seconds())
            if self.request(("init", self.sshfs.targetpath)) != "ACK":
                raise Exception("internal error while initializing the remote ssh xattr proxy.")

        def request(self, command):
            _bench1 = datetime.datetime.now()
            rawcmd = base64.b64encode(repr(command).encode(errors='backslashreplace'))
            self.sin.write((rawcmd+b"\n"))
            self.sin.flush()
            rawans = self._waitanswer(endstring=" DONE")[:-5].strip()
            doraise = False
            if rawans.endswith(" RAISE"):
                doraise = True
                rawans = rawans[:-6]
            ans = base64.b64decode(rawans.encode()).decode()
            self._benchmark += (datetime.datetime.now() - _bench1)
            if doraise:
                try:
                    ex = eval(ans)
                except Exception:
                    ex = Exception("Unserializable exception from remote ssh xattr proxy: " + ans)
                raise ex
            return eval(ans)

        def shutdown(self):
            try:
                self.request(("shutdown",))
            except Exception:
                pass

    def getsshxattrproxy(self):
        if self.sshxattrproxy is None:
            self.sshxattrproxy = SshfsFilesystem._SshXattrProxy(self)
        return self.sshxattrproxy

    def listxattrkeys(self, path):
        return self.getsshxattrproxy().request(("listxa", path))

    def getxattrvalue(self, path, key):
        return self.getsshxattrproxy().request(("getxa", path, key))

    def setxattrvalue(self, path, key, value):
        return self.getsshxattrproxy().request(("setxa", path, key, value))

    def unsetxattrvalue(self, path, key):
        return self.getsshxattrproxy().request(("unsetxa", path, key))

