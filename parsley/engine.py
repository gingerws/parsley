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

##@package parsley.engine
## The engine which abstractly executes arbitrary synchronization tasks.

import os
import time
import sys
import traceback
import glob
from parsley.logger.severity import Severity
from parsley.runtime.returnvalue import ReturnValue
from parsley.runtime.runtime import RuntimeData
# noinspection PyUnresolvedReferences
from parsley.runtime.commonimports import *


## The parsley engine. It is the lowest (or higest, if you will) layer, which coordinates all the synchronization
## work.
class Engine:

    ## Executes the selected synchronization tasks.
    ##@param syncs a list of synchronization tasks existing in your configuration.
    ##@param datadir which directory to use for persistent control data (file lists, ...)
    ##@param syncname which sync task shall be executed (None: all)
    ##@param logging list of loggers of logging output
    ##@param throwexceptions should exceptions be raised in error case?
    def execute(self, syncs, datadir, syncname=None, logging=[],  throwexceptions=False):
        runtime = RuntimeData(datadir, logging)
        runtime.warner.setscope(syncs)
        if syncname:
            syncstack = []
            for s in syncs:
                if s.fullname == syncname:
                    syncstack.append([s, True])
                    break
        else:
            syncstack = [[x, False] for x in syncs]
        while len(syncstack) > 0:
            (sync, force) = syncstack[0]
            syncstack = syncstack[1:]
            if self.executesync(sync, runtime, force, throwexceptions):
                if runtime.changed_flag:
                    for othersync in [s for s in syncs if s != sync and s.name == sync.name]:
                        instack = [x for x in syncstack if x[0] == othersync]
                        if len(instack) == 0:  # not othersync in syncstack:
                            syncstack.append([othersync, True])
                        else:
                            instack[0][1] = True
        runtime.warner.end()
        runtime.shutdown()
        with open(runtime.mydir + "/heartbeat", "w") as f:
            pass
        return runtime.retval

    def executesync(self, sync, runtime, force=False, throwexceptions=True):
        runtime.changed_flag = False
        enabledpreps = []
        stopped = False
        interrupted = None
        runtime.currentsync = sync
        runtime.lastsyncsuccess = None
        if force or not runtime.warner.shall_skip(sync):
            runtime.log(verb="Begin preparing", severity=Severity.DEBUG)
            try:  # for ctrl+c
                try:
                    sync.initialize(runtime)
                except Exception as e:
                    runtime.lastsyncsuccess = False
                    e_full = traceback.format_exc()
                    runtime.log(verb="Error", comment="while initializing: " + str(e),
                                severity=Severity.ERROR, symbol="E")
                    runtime.log(subject="Callstack", comment=e_full, severity=Severity.DEBUG, symbol="E")
                    runtime.retval |= ReturnValue.ERROR_INITIALIZATION
                    stopped = True
                    if throwexceptions:
                        raise
                if not stopped:
                    for p in sync.preparations:
                        itry = p.tries
                        succ = False
                        while itry > 0 and not succ:
                            try:
                                if p.ensuredisabledbefore():
                                    try:
                                        st = p.getstate(runtime)
                                    except Exception:
                                        st = True
                                        runtime.log(verb="Error",
                                                    comment="while getting preparation state: " + traceback.format_exc(),
                                                    severity=Severity.DEBUG, symbol="E")
                                        if throwexceptions:
                                            raise
                                    if st:
                                        runtime.log(comment="Preparation not disabled before enabling",
                                                    severity=Severity.DEBUG, symbol="E")
                                        raise Exception()
                                try:
                                    enabledpreps.append(p)
                                    p.enable(runtime)
                                    if p.ensureenabled():
                                        try:
                                            st = p.getstate(runtime)
                                        except Exception:
                                            st = False
                                            runtime.log(verb="Error",
                                                comment="while getting preparation state: " + traceback.format_exc(),
                                                severity=Severity.DEBUG, symbol="E")
                                            if throwexceptions:
                                                raise
                                        if not st:
                                            raise Exception("Preparation disabled after enabling")
                                    succ = True
                                except Exception:
                                    runtime.log(verb="Error",
                                                comment="while enabling preparation: " + traceback.format_exc(),
                                                severity=Severity.DEBUGVERBOSE, symbol="E")
                                    raise
                            except Exception:
                                if throwexceptions:
                                    raise
                            itry -= 1
                            if not succ:
                                time.sleep(2)
                        if not succ:
                            runtime.retval |= ReturnValue.ERROR_PREPARATION
                            runtime.log(comment="Enabling preparation failed after retry count exhausted",
                                        severity=Severity.DEBUG)
                            stopped = True
                            break
                if not stopped:
                    try:
                        runtime.log(verb="Start executing", severity=Severity.DEBUG)
                        try:
                            crashed = True
                            sync.execute(runtime)
                            crashed = False
                        finally:
                            sync.shutdown(runtime, crashed)
                        runtime.lastsyncsuccess = True
                        runtime.log(verb="Successfully executed", severity=Severity.DEBUG)
                        runtime.warner.successfulcall(sync)
                    except Exception as e:
                        runtime.lastsyncsuccess = False
                        e_full = traceback.format_exc()
                        runtime.log(verb="Error", comment="while executing: " + str(e),
                                    severity=Severity.ERROR, symbol="E")
                        runtime.log(subject="Callstack", comment=e_full, severity=Severity.DEBUG, symbol="E")
                        runtime.retval |= ReturnValue.ERROR_EXECUTION
                        if throwexceptions:
                            raise
            except KeyboardInterrupt as ki:
                interrupted = ki
                runtime.log(verb="Process interrupted", severity=Severity.ERROR)
            runtime.log(verb="Start disabling preparations", severity=Severity.DEBUG)
            for p in enabledpreps[::-1]:
                succ = False
                itry = p.tries
                while itry > 0 and not succ:
                    try:
                        try:
                            p.disable(runtime)
                            if p.ensuredisabledafter():
                                try:
                                    st = p.getstate(runtime)
                                except Exception:
                                    runtime.log(verb="Error",
                                                comment="while getting preparation state: " + traceback.format_exc(),
                                                severity=Severity.DEBUG, symbol="E")
                                    st = True
                                if st:
                                    raise Exception("preparation not stopped after disabling")
                            succ = True
                        except KeyboardInterrupt as ki:
                            interrupted = ki
                            runtime.log(verb="Process interrupted", severity=Severity.ERROR)
                        except Exception:
                            runtime.log(verb="Error", comment="while disabling preparation: " + traceback.format_exc(),
                                        severity=Severity.DEBUG, symbol="E")
                            if throwexceptions:
                                raise
                        itry -= 1
                        if not succ:
                            time.sleep(2)
                    except BaseException:
                        if throwexceptions:
                            raise
                if not succ:
                    runtime.retval |= ReturnValue.ERROR_UNPREPARATION
                    runtime.log(verb="Disabling preparation failed after retry count exhausted",
                                severity=Severity.ERROR)
                    break
            if interrupted:
                raise interrupted
            return True
        else:
            runtime.log(verb="Task execution skipped", severity=Severity.DEBUG)
            return False


def _cmdline(args):
    def _next():
        nonlocal c
        nonlocal args
        v = args[c] if c < len(args) else None
        c += 1
        return v

    class Cmdline:
        pass

    c = 1
    values = {}
    _p = _next()
    forcesyncs = []
    lockpid = None
    values["forcesyncs"] = forcesyncs
    while _p is not None:
        if _p[0:2] != "--": raise Exception("parse error: " + _p)
        p = _p[2:]
        if p == "config":
            values["cfgfile"] = _next()
        elif p == "sync":
            values[p] = _next()
        elif p == "datadir":
            values[p] = _next()
        elif p == "prependcfg":
            values[p] = _next()
        elif p == "lock" or p == "unlock":
            values[p] = True
            if p == "lock":
                values["lockpid"] = _next() or "-1"
        elif p == "forcesync":
            forcesyncs += [_next()]
        elif p == "listsyncs":
            values[p] = True
        else:
            raise Exception("unknown parameter: '" + p + "'")
        _p = _next()
    r = Cmdline()
    r.cfgs = values.keys()
    for k in values:
        setattr(r, k, values[k])
    return r


## Locks a lockfile for synchronization.
def lock(fle, lockpid=-1):
    if os.path.isfile(fle):
        with open(fle, "r") as f:
            try:
                lpid = int(f.readline())
                if lpid == -1:
                    return False
            except ValueError:
                return False
        cmdline = None
        try:            
            with open("/proc/"+str(lpid)+"/cmdline", "r") as f:
                cmdline = f.readline()
                if "parsley" in cmdline:
                    return False
        except IOError:
            pass
        if not cmdline:
            os.unlink(fle)        
    try:
        fd = os.open(fle, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        os.write(fd, str(lockpid).encode())
        os.close(fd)
        return True
    except OSError:
        return False


## Unlocks a lockfile.
def unlock(fle):
    os.remove(fle)


## Main method for execution from command line.
def main():
    retval = 0
    cmdline = _cmdline(sys.argv)
    if not "cfgfile" in cmdline.cfgs:
        raise Exception("no config file given with --config")
    with open(cmdline.cfgfile, "r") as f:
        cfg = "".join(f.readlines())
    if "prependcfg" in cmdline.cfgs:
        cfg = cmdline.prependcfg + "\n" + cfg
    datadir = cmdline.datadir if ("datadir" in cmdline.cfgs) else os.path.expanduser("~/.parsley.d")
    if not os.path.exists(datadir):
        os.makedirs(datadir)
    for forcesync in cmdline.forcesyncs:
        c = None
        for fn in glob.glob(datadir + "/lastsuccess." + forcesync):
            fn = os.path.abspath(fn)
            with open(fn, "r") as f:
                c = f.readlines()
            if c is not None:
                if len(c) > 0:
                    c[0] = " " + c[0]
                    with open(fn, "w") as f:
                        for cl in c: f.write(cl)
    if "sync" in cmdline.cfgs:
        if lock(datadir + "/lock", os.getpid()):
            try:
                g = globals()
                l = locals()
                logging = []
                g["syncs"] = []
                g["logging"] = logging
                exec(cfg, globals(), globals())
                syncname = cmdline.sync if cmdline.sync != "ALL" else None
                retval = Engine().execute(g["syncs"], datadir, syncname, logging)
            finally:
                unlock(datadir + "/lock")
    elif "lock" in cmdline.cfgs:
        i = 0
        while not lock(datadir + "/lock", cmdline.lockpid):
            if i % 20 == 0:
                print("Waiting for other instance...")
            i += 1
            time.sleep(1)
    elif "unlock" in cmdline.cfgs:
        unlock(datadir + "/lock")
    elif "listsyncs" in cmdline.cfgs:
        g = globals()
        l = locals()
        syncs = []
        g["syncs"] = syncs
        g["logging"] = []
        oout = sys.stdout  # preventing logger spam in output
        sys.stdout = nullout = open("/dev/null", "w")
        exec(cfg, g, l)
        sys.stdout = oout
        nullout.close()
        for sync in syncs:
            print(sync.fullname)
    sys.exit(retval)
