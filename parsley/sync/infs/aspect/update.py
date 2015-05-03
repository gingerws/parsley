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

import os
from parsley.logger.severity import Severity
from parsley.sync.infs import ActionControl, Filesystem
from parsley.sync.infs.syncmachine import SyncHooks
from parsley.sync.infs.aspect import Aspect


## Default handling for updating files.
class DefaultUpdateFile(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Skips a file entry if the files have identical mtime in both filesystems.
    @staticmethod
    def _skip_identical(fs, machine):
        def _x(srcfs, path, runtime):
            dstexists = machine.filelists[fs].exists(path)
            if dstexists:
                dstmtime = machine.filelists[fs].getmtime(path)
                srcmtime = machine.filelists[srcfs].getmtime(path)
                if dstmtime == srcmtime:
                    return ActionControl.SKIP
        return _x

    ## Checks if a file entry stays in an update conflict (by mtime comparisons) and if so, log a warning and skip
    ## the entry.
    @staticmethod
    def _log_and_skip_updateconflict(fs, machine):
        def _x(srcfs, path, runtime):
            oldsrcexists = machine.lastfilelists[srcfs].exists(path)
            srcmtime = machine.filelists[srcfs].getmtime(path)
            if oldsrcexists:
                oldsrcmtime = machine.lastfilelists[srcfs].getmtime(path)
                oldsrcsize = machine.lastfilelists[srcfs].getsize(path)
            else:
                oldsrcmtime = None
                oldsrcsize = None
            olddstexists = machine.lastfilelists[fs].exists(path)
            if olddstexists:
                olddstmtime = machine.lastfilelists[fs].getmtime(path)
                olddstsize = machine.lastfilelists[fs].getsize(path)
            else:
                olddstmtime = None
                olddstsize = None
            dstexists = machine.filelists[fs].exists(path)
            if dstexists:
                dstmtime = machine.filelists[fs].getmtime(path)
            else:
                dstmtime = None
            if (not dstexists) or \
                    ((not oldsrcexists) and (not olddstexists) and srcmtime == dstmtime) or \
                    (oldsrcexists and olddstexists and \
                                 oldsrcmtime == olddstmtime and olddstmtime == dstmtime):
                return
            else:
                machine.logproblem(fs, path, runtime, verb="has update conflict")
                machine.logproblem(fs, path, runtime, comment="dstexists={dstexists}, oldsrcexists={oldsrcexists}, olddstexists={olddstexists}, srcmtime={srcmtime}, dstmtime={dstmtime}, oldsrcmtime={oldsrcmtime}, olddstmtime={olddstmtime}".format(**locals()), severity=Severity.DEBUG)
                return ActionControl.SKIP
        return _x

    ## Updates the file in the filesystem.
    @staticmethod
    def _updatefile(fs, machine):
        def _x(srcfs, path, runtime):
            srcpath = srcfs.getfulllocalpath(path)
            dstexists = machine.filelists[fs].exists(path)
            expecteddstmtime = machine.lastfilelists[fs].getmtime(path)
            fmtime, fsize = fs.copyfile(srcpath, path, expecteddstmtime)
            if fmtime is None: # skipped for this time (maybe due to a dirty copy)
                machine.logproblem(fs, path, runtime, verb="skipped this time")
                # set file metadata on source side back to old known values for avoiding conflicts in subsequent runs...
                fsize = machine.lastfilelists[srcfs].getsize(path)
                fmtime = machine.lastfilelists[srcfs].getmtime(path)
                if fsize is None:
                    machine.filelists[srcfs].removefile(path)
                else:
                    machine.filelists[srcfs].foundfile(path, Filesystem.File, fsize, fmtime, None)
            else:
                dn = os.path.dirname(path)
                mylist = machine.filelists[fs]
                while dn != "/" and not mylist.exists(dn):
                    mtime = fs.getmtime(dn)
                    size = fs.getsize(dn)
                    mylist.updatefile(dn, Filesystem.Directory, size, mtime, None)
                    dn = os.path.dirname(dn)
                if dstexists:
                    machine.logupdate(fs, path, runtime, comment="on "+fs.name)
                else:
                    machine.logcreate(fs, path, runtime, comment="on "+fs.name)
                machine.filelists[fs].updatefile(path, Filesystem.File, fsize, fmtime, None)
                machine.filelists[srcfs].updatefile(path, Filesystem.File, fsize, fmtime, None)
                runtime.changed_flag = True
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onupdatefile, 20000, DefaultUpdateFile._skip_identical(fs, machine))
            machine.addhook(fs, SyncHooks.onupdatefile, 40000, DefaultUpdateFile._log_and_skip_updateconflict(fs, machine))
            machine.addhook(fs, SyncHooks.onupdatefile, 60000, DefaultUpdateFile._updatefile(fs, machine))


## Default handling for updating links.
class DefaultUpdateLink(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Skips a link entry if it has the same link target in both filesystems.
    @staticmethod
    def _skip_identical(fs, machine):
        def _x(srcfs, path, runtime):
            dstexists = machine.filelists[fs].exists(path)
            if dstexists:
                dsttgt = fs.getlinktarget(path)
                srctgt = srcfs.getlinktarget(path)
                if dsttgt == srctgt:
                    return ActionControl.SKIP
        return _x

    ## Checks if a link entry stays in an update conflict (by link target comparisons) and if so, log a warning and skip
    ## the entry.
    @staticmethod
    def _log_and_skip_updateconflict(fs, machine):
        def _x(srcfs, path, runtime):
            oldsrcexists = machine.lastfilelists[srcfs].exists(path)
            if oldsrcexists:
                oldsrctgt = machine.lastfilelists[srcfs].getparam(path)
            olddstexists = machine.lastfilelists[fs].exists(path)
            if olddstexists:
                olddsttgt = machine.lastfilelists[fs].getparam(path)
            dstexists = machine.filelists[fs].exists(path)
            if dstexists:
                dsttgt = fs.getlinktarget(path)
            if (not dstexists) or \
                    (oldsrcexists and olddstexists and \
                                 oldsrctgt == olddsttgt and olddsttgt == dsttgt):
                return
            else:
                machine.logproblem(fs, path, runtime, verb="has update conflict")
                return ActionControl.SKIP
        return _x

    ## Updates the link in the filesystem.
    @staticmethod
    def _updatelink(fs, machine):
        def _x(srcfs, path, runtime):
            lnktgt = srcfs.getlinktarget(path)
            existed = False
            if fs.getftype(path) == Filesystem.Link:
                fs.removelink(path)
                existed = True
            fs.createlink(lnktgt, path)
            if existed:
                machine.logupdate(fs, path, runtime, comment="on "+fs.name)
            else:
                machine.logcreate(fs, path, runtime, comment="on "+fs.name)
            machine.filelists[fs].updatefile(path, Filesystem.Link, None, None, lnktgt)
            runtime.changed_flag = True
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onupdatelink, 20000, DefaultUpdateLink._skip_identical(fs, machine))
            machine.addhook(fs, SyncHooks.onupdatelink, 40000, DefaultUpdateLink._log_and_skip_updateconflict(fs, machine))
            machine.addhook(fs, SyncHooks.onupdatelink, 60000, DefaultUpdateLink._updatelink(fs, machine))
