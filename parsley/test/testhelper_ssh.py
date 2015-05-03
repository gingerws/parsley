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

##@package parsley.test.testhelper_ssh
## Some helper functions over ssh filesystems.

import random
import signal
import shutil
import subprocess
import threading
import time
import datetime
import os
from parsley.test.testhelper_common import *

def _iptables(cmd):
    try:
        subprocess.call(["sudo", "iptables"] + cmd.split(" "))
    except Exception:
        pass
    try:
        subprocess.call(["sudo", "ip6tables"] + cmd.split(" "))
    except Exception:
        pass


class RateLimiter:
    def __init__(self):
        pass

    def __enter__(self):
        _iptables("-N PARSLEYTEST11")
        _iptables("-I INPUT -i lo -p tcp --dport 42921 -j PARSLEYTEST11")
        _iptables("-A PARSLEYTEST11 -m limit --limit 5000/min -j ACCEPT")
        _iptables("-A PARSLEYTEST11 -j DROP")
        return self

    def __exit__(self, type, value, traceback):
        _iptables("-D INPUT -i lo -p tcp --dport 42921 -j PARSLEYTEST11")
        _iptables("-F PARSLEYTEST11")
        _iptables("-X PARSLEYTEST11")


class TemporarySshFs:
    def __init__(self, mydir):
        self.mydir = mydir
        self.sshdpath = "/usr/sbin/sshd"
        self.sftpserverpath = "/usr/lib/sftp-server"

    def __enter__(self):
        sshdconfig = """
            Port 42921
            AddressFamily any
            ListenAddress 0.0.0.0
            ListenAddress ::
            HostKey {MYDIR}/hostkey
            UsePrivilegeSeparation no
            AuthorizedKeysFile {MYDIR}/parsley.authorizedkeys
            PermitEmptyPasswords yes
            UsePAM yes
            Compression no
            PidFile {MYDIR}/sshd.pid
            Subsystem	sftp	{SFTPSERVERPATH}
        """.format(MYDIR=self.mydir, SFTPSERVERPATH=self.sftpserverpath)
        with open(self.mydir + "/sshdconfig", "w") as f:
            f.write(sshdconfig)
        subprocess.call(["ssh-keygen", "-t", "rsa", "-f", self.mydir + "/hostkey", "-N", ""])
        subprocess.call(["ssh-keygen", "-t", "rsa", "-N", "", "-f", self.mydir + "/loginkey"])
        subprocess.call([self.sshdpath, "-f", self.mydir + "/sshdconfig"])
        shutil.copy(self.mydir + "/loginkey.pub", self.mydir + "/parsley.authorizedkeys")
        return self

    def __exit__(self, type, value, traceback):
        try:
            with open(self.mydir + "/sshd.pid", "r") as f:
                pid = int("".join(f.readlines()))
                os.kill(pid, signal.SIGINT)
        except Exception as e:
            print("servers not killed: ", e)


class Disturbator:
    def __init__(self, conn_oh, tempssh, mydir, disturbinterval=16):
        self.conn_oh = conn_oh
        self.mydir = mydir
        self.starttime = None
        self.terminated = False
        self.on = False
        self.tempssh = tempssh
        self.t = None
        self.disturbinterval = disturbinterval

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def d_iptables(self):
        m = random.choice(["REJECT", "DROP"])
        _iptables("-I PARSLEYTEST11 -p tcp --dport 42921 -j " + m)
        time.sleep(random.randrange(self.disturbinterval) + 3)
        _iptables("-D PARSLEYTEST11 -p tcp --dport 42921 -j " + m)

    def d_killmounter(self):
        pids = [int(x) for x in os.listdir('/proc') if x.isdigit()]
        pidnames = {}
        for pid in pids:
            try:
                with open("/proc/" + str(pid) + "/cmdline", "r")as f:
                    pidname = f.readline()
                pidnames[pid] = pidname
            except Exception as e:
                pass
        for pid in pidnames:
            n = pidnames[pid]
            if n.find("42921") > -1 and n.find("ftp") > -1:
                os.kill(pid, signal.SIGTERM)
                print("Terminate pid " + str(pid))

    def d_killserver(self):
        with open(self.mydir + "sshd.pid", "r") as f:
            sshdpid = int(f.readline())
        pids = []
        npids = [sshdpid]
        while len(npids) > 0:
            pids += npids
            nnpids = []
            for npid in npids:
                try:
                    x = subprocess.check_output(["ps", "-o", "pid ", "--no-headers", "--ppid", str(npid)]).split(
                        b"\n")
                    for xx in x:
                        nnpids += [int(xx)]
                except Exception:
                    pass
            npids = nnpids
        for j in pids:
            subprocess.call(["sudo", "kill", "-9", str(j)])
        print("Killed sshd " + ",".join([str(j) for j in pids]))
        time.sleep(random.randrange(self.disturbinterval) + 3)
        subprocess.call([self.tempssh.sshdpath, "-f", self.mydir + "/sshdconfig"])  # copied

    def disturb(self):
        try:
            random.choice([self.d_iptables, self.d_killmounter, self.d_killserver])()
        except Exception as e:
            print(e)

    def thread(self):
        while not self.terminated:
            while (not self.terminated) and (not self.on):
                time.sleep(0.1)
            dur = (1 + random.randrange(2)) * self.conn_oh * 0.8 + random.randrange(self.disturbinterval)
            for w in range(int(dur)):
                time.sleep(1)
                if self.terminated:
                    return
            print("begin disturbing process")
            self.disturb()
            print("stop disturbing process")

    def start(self):
        self.on = True
        self.t = threading.Thread(target=self.thread, args=())
        self.t.start()

    def terminate(self):
        self.terminated = True


def measure_network():
    os.mkdir(getmydir() + "_s")
    curr = 13000.0
    dur = None
    print("determining a good filesize for 10 seconds transfer time")
    print("determining connection overhead")
    mins = 1000000
    maxs = 0
    write2file("s/_dummym", "")
    write2file("m/_dummys", "")
    SYNC()
    for i in range(3):
        t1 = datetime.datetime.now()
        SYNC()
        t2 = datetime.datetime.now()
        _dur = (t2 - t1).total_seconds()
        if _dur < mins:
            mins = _dur
        if _dur > maxs:
            maxs = _dur
    RESET()
    os.mkdir(mydir + "_s")
    if maxs - mins > 2:
        print("WARNING: sloppy system!")
    ohdur = (maxs + mins) * 0.5
    print("overhead duration: " + str(ohdur) + "s (deviation: " + str(maxs - mins) + ")")
    while (dur is None) or not (9 < dur < 13):
        if not os.path.exists(getmydir() + "m"):
            os.mkdir(getmydir() + "m")
        with open(getmydir() + "m/b", "w") as f:
            l = "1" * 1024
            for i in range(int(curr)):
                f.write(l)
        write2file("s/_dummy", "")
        if curr >= 0.6 * 1024 * 1024 * 1024:
            scurr = str(curr / (1024.0 * 1024 * 1024)) + "TB"
        elif curr >= 0.6 * 1024 * 1024:
            scurr = str(curr / (1024.0 * 1024)) + "GB"
        elif curr >= 0.6 * 1024:
            scurr = str(curr / 1024.0) + "MB"
        else:
            scurr = str(curr) + "KB"
        print("testing with " + scurr)
        t1 = datetime.datetime.now()
        SYNC()
        t2 = datetime.datetime.now()
        dur = max((t2 - t1).total_seconds() - ohdur, 0.2)
        print("we took " + str(dur) + " seconds")
        for10secs = int(curr)
        curr *= (11.0 / dur)
        RESET()
    print("use the last value")
    if curr > 1024 * 25:
        print("WARNING: the rate limiter does not seem to work; huge data amounts can occur!")
    return for10secs, ohdur