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

##@package parsley.test.testhelper_common
## Some common helper functions for implementing tests.

import os
import subprocess
import shutil
import sys
import time

_testfile = os.path.abspath(sys.argv[0])
def gettestfile():
    return _testfile


def gettestrootdir():
    return os.path.dirname(gettestfile())


def getmydir(): # must be within the homedir otherwith sshd fails
    return gettestrootdir() + "/testing/"


def write2file(p, m):
    _p = mydir + p
    d = os.path.dirname(_p)
    if not os.path.exists(d):
        os.makedirs(d)
    with open(_p, "wt") as ff:
        ff.write(m + "\n")


def readfile(p):
    r = ""
    try:
        with open(mydir + p, "rt") as ff:
            r += ff.readline()
    except Exception:
        pass
    return r.strip()


def readtrashedfile(p):
    si = p.index("/")
    return readfile(p[:si] + "/.parsley.control/deleted_files" + p[si:])


def fileexiststrashed(p):
    si = p.index("/")
    return fileexists(p[:si] + "/.parsley.control/deleted_files" + p[si:])


def link(s, d):
    try:
        if os.path.islink(mydir + d): os.remove(mydir + d)
    except Exception:
        pass
    os.symlink(s, mydir + d)


def islink(s):
    try:
        return os.readlink(mydir + s)
    except Exception:
        return None


def trashed(p, onlybool=False):
    r = ""
    try:
        ip = p.find("/")
        p1 = p[0:ip]
        p2 = p[ip + 1:]
        x = os.path.abspath(mydir + p1 + "/.parsley.control/deleted_files/" + p2)
        if os.path.exists(x):
            if onlybool:
                return True
            with open(x, "rt") as ff:
                r += ff.readline()
    except Exception:
        pass
    if onlybool:
        return False
    return r.strip() if r != "" else None


def deletefile(p):
    try:
        os.remove(mydir + p)
    except Exception:
        pass


def deletedir(p):
    try:
        shutil.rmtree(mydir + p)
    except Exception as e:
        print(e)


def filesindir(p, _res=None):
    res = [] if _res is None else _res
    for x in os.listdir(mydir + p):
        if os.path.isfile(mydir + p + "/" + x):
            res.append(x)
        elif os.path.isdir(mydir + p + "/" + x):
            filesindir(p + "/" + x, res)
    return res


def listdir(p):
    try:
        return os.listdir(mydir + p)
    except Exception:
        return []


def verify(c, m):
    if c:
        print("\033[42m\033[30mpassed: %s\033[0m" % (m,))
    else:
        print("\033[41mERROR: %s NOT PASSED\033[0m" % (m,))


def isdir(p):
    return os.path.isdir(mydir + p)


def fileexists(p):
    return os.path.isfile(mydir + p)


def fileexistspattern(p):
    dr = os.path.dirname(mydir + p)
    fn = os.path.basename(p)
    for x in os.listdir(dr):
        if x.find(fn) != -1:
            return True
    return False


def exists(p):
    return os.path.exists(mydir + p)


def haslogentry(p, verb=None):
    with open(mydir + "log.txt", "rt") as ff:
        cont = ff.readlines()
    for ll in cont:
        if ll.find(p) > -1 and (verb is None or ll.find(verb) > -1):
            return True
    return False


# noinspection PyPep8Naming
def SYNC():
    global _comm_i
    if os.path.exists(mydir + "log.txt"):
        os.remove(mydir + "log.txt")
    cwd = os.getcwd()
    os.chdir(mydir)
    try:
        if 0 != subprocess.call(
                [gettestrootdir() + "/../../parsley.py", "--config", gettestfile(), "--sync", "ALL", "--datadir",
                 mydir + "datadir", "--prependcfg", prependcfg]):
            raise Exception("error in parsley call (possibly wanted by the test)")
    finally:
        os.chdir(cwd)
        if os.path.isfile(mydir + "log.txt"):
            shutil.copy(mydir + "log.txt", mydir + "test.log.{0}.txt".format(_comm_i))
    _comm_i += 1


# noinspection PyPep8Naming
def RESET(removebefore=False):
    if removebefore and os.path.exists(mydir):
        shutil.rmtree(mydir)
    if not os.path.exists(mydir):
        os.mkdir(mydir)
    for x in os.listdir(mydir):
        fx = mydir + "/" + x
        if os.path.isdir(fx):
            shutil.rmtree(fx)

try:
    cols = int(subprocess.check_output(["tput", "cols"]))
except Exception:
    cols = 80

prependcfg = "mydir=\"" + getmydir() + """\"
logging.append( Logger(loggerout=FilestreamLoggerout(filename=mydir+"log.txt"),
        formatter=PlaintextLogformat(maxlen={cols}), minseverity=Severity.DEBUGVERBOSE, maxseverity=Severity.ERROR))
logging.append( Logger(loggerout=FilestreamLoggerout(),
        formatter=PlaintextLogformat(maxlen={cols}, color=4), minseverity=Severity.DEBUGVERBOSE, maxseverity=Severity.ERROR))
""".format(cols=cols)

mydir = getmydir()
_comm_i = 1

