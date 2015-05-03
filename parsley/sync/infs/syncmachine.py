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

##@package parsley.sync.infs.syncmachine
## Some inner parts of the parsley.sync.infs.InFsSync implementation, also contains the event hook definitions.

from parsley.logger.severity import Severity
from parsley.sync.infs.common import *
from parsley.sync.infs.entrylist import EntryList, CombinedEntryList


class SyncHooks:

    ## The begin of the complete sync run.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    onbeginsync = object()

    ## The very begin of processing a directory.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    onbeginupdatedir = object()

    ## This hook collects all files from all filesystems in this dir.
    ##
    ## Handlers are called 'grouped by filesystem first' for all filesystems.
    ##
    ## Additional parameter is the list it may fill.
    onlistdir = object()

    ## Returns a key (typically int) which indicates how up-to-date the entry is on that filesystem.
    ## The engine will try to mirror the winner to all other places.
    ##
    ## May return parsley.sync.infs.common.ElectionControl.SKIP for skipping this file.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    onelectmaster = object()

    ## When a real master is elected (not SKIPped), this event occurs.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    onmasterelected = object()

    ## The typeconflict resolution between the master and conflicting slave from the master's perspective.
    ##
    ## May return parsley.sync.infs.common.ConflictResolution.FORCE_SYNC,
    ## parsley.sync.infs.common.ConflictResolution.SKIP or parsley.sync.infs.common.ConflictResolution.NO_IDEA.
    ontypeconflictmaster = object()

    ## The typeconflict resolution between the master and conflicting slave from the slave's perspective.
    ##
    ## May return parsley.sync.infs.common.ConflictResolution.FORCE_SYNC,
    ## parsley.sync.infs.common.ConflictResolution.SKIP or parsley.sync.infs.common.ConflictResolution.NO_IDEA.
    ontypeconflictslave = object()

    ## Updates (create or overwrite) a file on a slave by the master.
    ##
    ## May return parsley.sync.infs.common.ActionControl.SKIP (skipping other hooks *for this destination filesystem*).
    ##
    ## Called once for each filesystem which needs an update.
    ##
    ## Handlers are called 'grouped by filesystem first'.
    ##
    ## Additional parameters are the master filesystem and the target filesystem.
    onupdatefile = object()

    ## Updates (create or overwrite) a link on a slave by the master.
    ##
    ## May return parsley.sync.infs.common.ActionControl.SKIP (skipping other hooks *for this destination filesystem*).
    ##
    ## Called once for each filesystem which needs an update.
    ##
    ## Handlers are called 'grouped by filesystem first'.
    ##
    ## Additional parameters are the master filesystem and the target filesystem.
    onupdatelink = object()

    ## Removes a file on a slave on behalf of the master.
    ##
    ## May return parsley.sync.infs.common.ActionControl.SKIP (skipping other hooks *for this destination filesystem*).
    ##
    ## Called once for each filesystem which needs removal.
    ##
    ## Handlers are called 'grouped by filesystem first'.
    ##
    ## Additional parameters are the master filesystem and the target filesystem.
    onremovefile = object()

    ## Removes a link on a slave on behalf of the master.
    ##
    ## May return parsley.sync.infs.common.ActionControl.SKIP (skipping other hooks *for this destination filesystem*).
    ##
    ## Called once for each filesystem which needs removal.
    ##
    ## Handlers are called 'grouped by filesystem first'.
    ##
    ## Additional parameters are the master filesystem and the target filesystem.
    onremovelink = object()

    ## Removes a directory on a slave on behalf of the master.
    ##
    ## May return parsley.sync.infs.common.ActionControl.SKIP (skipping other hooks *for this destination filesystem*).
    ##
    ## Called once for each filesystem which needs removal.
    ##
    ## Handlers are called 'grouped by filesystem first'.
    ##
    ## Additional parameters are the master filesystem and the target filesystem.
    onremovedir = object()

    ## After processing a file.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    ##
    ## Additional parameter is the master filesystem.
    onendprocessfile = object()

    ## After processing a link.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    ##
    ## Additional parameter is the master filesystem.
    onendprocesslink = object()

    ## The very end of processing a directory.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    onendupdatedir = object()

    ## The end of the complete sync run.
    ##
    ## Handlers are called 'grouped by event handler first' for all filesystems.
    onendsync = object()

    ## Logs object creation.
    onlogcreate = object()

    ## Logs object removal.
    onlogremove = object()

    ## Logs object updates.
    onlogupdate = object()

    ## Logs problems.
    onlogproblem = object()


## The state and some data structures for a full sync run at runtime. Register for all the hooks, which do
## the actual work. The static objects beginning with 'on' are keys for adding a hook to certain events.
class SyncMachine:

    def __init__(self, filesystems, task, runtime):
        self._handlers = {}
        self.filesystems = filesystems
        self.lastfilelistfilenames = {}
        self.lastfilelists = {}
        self.filelists = {}
        for fs in filesystems:
            self.lastfilelistfilenames[fs] = _y = runtime.mydir + "/lastfiles.{fullname}.{fsname}".format(
                fullname=task.fullname, fsname=fs.name)
            self.lastfilelists[fs] = _x = EntryList()
            _x.readfromfile(_y)
            _x = EntryList()
            _x.readfromfile(_y)
            self.filelists[fs] = CombinedEntryList(EntryList(), _x) # we actually track two lists here: one primary and one derived from the old list for crashes

    def shutdown(self, crashed):
        for fs in self.filesystems:
            if not crashed:
                self.filelists[fs].first.savetofile(self.lastfilelistfilenames[fs])
            else:
                self.filelists[fs].second.savetofile(self.lastfilelistfilenames[fs])

    def hookglobalaspects(self, aspects):
        for aspect in aspects:
            aspect.hook(self, True, self.filesystems)

    def hookfsaspects(self, fs, aspects):
        for aspect in aspects:
            aspect.hook(self, False, [fs])

    # fs is either single fs or list of fs's
    def _gethandlers(self, fs, name):
        if not isinstance(fs, list):
            fs = [fs]
        tmplist = []
        for _fs_i, _fs in enumerate(fs):
            try:
                tmplist += [((x[0], _fs_i), x[1], _fs) for x in self._handlers[_fs][name]]
            except KeyError:
                pass
        return [(y[1], y[2]) for y in sorted(tmplist, key=lambda x: x[0])]

    def addhook(self, fs, name, idx, fct):
        if not fs in self._handlers:
            self._handlers[fs] = {}
        if not name in self._handlers[fs]:
            self._handlers[fs][name] = []
        self._handlers[fs][name].append((idx, fct))

    def resolvetypeconflict(self, path, m, s, runtime):
        for hdlr, hdlr_fs in \
                    self._gethandlers(m, SyncHooks.ontypeconflictmaster) \
                        + self._gethandlers(s, SyncHooks.ontypeconflictslave):
            _r = hdlr(path, m, s, runtime)
            if _r == ConflictResolution.SKIP:
                return _r
            elif _r == ConflictResolution.FORCE_SYNC:
                return _r
            elif _r == ConflictResolution.NO_IDEA:
                pass
            else:
                raise Exception("program error: invalid return value of ontypeconflict... handler: " + str(_r))
        raise Exception(
            "program error: unresolved type conflict for '{path}' between {sm} and {ss}.".format(path=path, sm=str(m),
                                                                                                 ss=str(s)))

    def beginupdatedir(self, path, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onbeginupdatedir):
            hdlr(path, runtime)

    def endupdatedir(self, path, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onendupdatedir):
            hdlr(path, runtime)

    def beginsync(self, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onbeginsync):
            hdlr(runtime)

    def endsync(self, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onendsync):
            hdlr(runtime)

    def updatefile(self, srcfs, path, dstfs, runtime):
        for hdlr, hdlr_fs in self._gethandlers(dstfs, SyncHooks.onupdatefile):
            r = hdlr(srcfs, path, runtime)
            if r == ActionControl.SKIP:
                break

    def updatelink(self, srcfs, path, dstfs, runtime):
        for hdlr, hdlr_fs in self._gethandlers(dstfs, SyncHooks.onupdatelink):
            r = hdlr(srcfs, path, runtime)
            if r == ActionControl.SKIP:
                break

    def removefile(self, srcfs, path, dstfs, runtime):
        for hdlr, hdlr_fs in self._gethandlers(dstfs, SyncHooks.onremovefile):
            r = hdlr(srcfs, path, runtime)
            if r == ActionControl.SKIP:
                break

    def removelink(self, srcfs, path, dstfs, runtime):
        for hdlr, hdlr_fs in self._gethandlers(dstfs, SyncHooks.onremovelink):
            r = hdlr(srcfs, path, runtime)
            if r == ActionControl.SKIP:
                break

    def removedir(self, srcfs, path, dstfs, runtime, recursive=False):
        for hdlr, hdlr_fs in self._gethandlers(dstfs, SyncHooks.onremovedir):
            r = hdlr(srcfs, path, runtime, recursive)
            if r == ActionControl.SKIP:
                break

    def endprocessfile(self, srcfs, path, wasremoved, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onendprocessfile):
            hdlr(srcfs, path, wasremoved, runtime)

    def endprocesslink(self, srcfs, path, wasremoved, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onendprocesslink):
            hdlr(srcfs, path, wasremoved, runtime)

    def iteratedir(self, path, runtime):
        ret = set()
        for fs in self.filesystems:
            _ret = set()
            for hdlr, hdlr_fs in self._gethandlers(fs, SyncHooks.onlistdir):
                hdlr(path, _ret, runtime)
            ret = ret.union(_ret)
        return sorted(ret)

    def electmaster(self, path, runtime):
        curr = None
        currkey = None
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onelectmaster):
            r = hdlr(path, runtime)
            if r is not None:
                if r == ElectionControl.SKIP:
                    return r
                elif currkey is None or r > currkey:
                    currkey = r
                    curr = hdlr_fs
        if curr is not None:
            return curr
        else:
            raise Exception("program error: no result in master election for path '{path}'.".format(path=path))

    def masterelected(self, fs, path, runtime):
        for hdlr, hdlr_fs in self._gethandlers(self.filesystems, SyncHooks.onmasterelected):
            r = hdlr(fs, path, runtime)
            if r == ActionControl.SKIP:
                return r

    def logcreate(self, fs, subject, runtime, verb="created", comment="", symbol="+", severity=Severity.INFO):
        for hdlr, hdlr_fs in self._gethandlers(fs, SyncHooks.onlogcreate):
            hdlr(subject, runtime, verb, comment, symbol, severity)

    def logremove(self, fs, subject, runtime, verb="removed", comment="", symbol="-", severity=Severity.MOREIMPORTANT):
        for hdlr, hdlr_fs in self._gethandlers(fs, SyncHooks.onlogremove):
            hdlr(subject, runtime, verb, comment, symbol, severity)

    def logupdate(self, fs, subject, runtime, verb="updated", comment="", symbol="*", severity=Severity.IMPORTANT):
        for hdlr, hdlr_fs in self._gethandlers(fs, SyncHooks.onlogupdate):
            hdlr(subject, runtime, verb, comment, symbol, severity)

    def logproblem(self, fs, subject, runtime, verb="has problems", comment="", symbol="E", severity=Severity.ERROR):
        for hdlr, hdlr_fs in self._gethandlers(fs, SyncHooks.onlogproblem):
            hdlr(subject, runtime, verb, comment, symbol, severity)
