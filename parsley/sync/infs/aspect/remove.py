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
import time
import datetime
from parsley.logger.severity import Severity
from parsley.sync.infs import Filesystem
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Detects removed entries.
class DetectRemoval(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Detects if an entry is to be removed and if so, returns the current time as election key.
    @staticmethod
    def _electbymtime_removedentry(fs, machine):
        def _x(path, runtime):
            if not machine.filelists[fs].exists(path):
                existed = machine.lastfilelists[fs].exists(path)
                if existed:
                    _lmtime = machine.lastfilelists[fs].getmtime(path)
                    changedonotherplaces = False
                    for _fs in machine.filesystems:
                        if fs != _fs and _fs.exists(path):
                            amtime = _fs.getmtime(path)
                            if _lmtime != amtime:
                                changedonotherplaces = True
                                break
                            lexists = machine.lastfilelists[_fs].exists(path)
                            if lexists:
                                lmtime = machine.lastfilelists[_fs].getmtime(path)
                                if lmtime != amtime:
                                    changedonotherplaces = True
                                    break
                    if not changedonotherplaces:
                        return time.mktime(datetime.datetime.now().timetuple())
            return None
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onelectmaster, 40000, DetectRemoval._electbymtime_removedentry(fs, machine))


## Removes directories via the filesystem.
class DefaultRemoveDirs(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Removes a directory (recursively or safely) in the filesystem.
    @staticmethod
    def _removedir(fs):
        def _x(srcfs, path, runtime, recursive):
            fs.removedir(path, recursive)
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onremovedir, 50000, DefaultRemoveDirs._removedir(fs))


## Removes empty orphaned directories.
class RemoveOrphanedDirs(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Removes a directory in the filesystem if it is empty and was removed in another filesystem.
    def _remove_orphaned_dirs(fs, machine):
        def _x(path, runtime):
            for _fs in machine.filesystems:
                if fs != _fs:
                    if not _fs.exists(path) and machine.lastfilelists[_fs].exists(path):
                        if fs.exists(path) and len(fs.listdir(path)) == 0:
                            fs.removedir(path)
                            machine.filelists[fs].removefile(path)
                        break
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onendupdatedir, 50000, RemoveOrphanedDirs._remove_orphaned_dirs(fs, machine))


## Cleans up the trash bin.
class CleanupTrashBin(Aspect):
    def __init__(self, trashdelay=datetime.timedelta(days=7)):
        Aspect.__init__(self)
        self.trashdelay = trashdelay

    ## Cleans up files in the trashbin control directory which fulfill certain conditions.
    @staticmethod
    def _cleanup_trashbin(fs, machine, trashdelay):
        def _x(path, runtime):
            if path == "":
                runtime.log(verb="begins cleaning up the trash bin", severity=Severity.DEBUG)
                def helper1(ppath, fpath, spath):
                    if fs.exists(fpath):
                        for x in fs.listdir(fpath):
                            px = ppath + "/" + x
                            fx = fpath + "/" + x
                            sx = spath + "/" + x
                            fxtype = fs.getftype(fx)
                            if fxtype == Filesystem.Directory:
                                helper1(px, fx, sx)
                            else:
                                remove = True
                                if fs.exists(sx):
                                    deltime = fs.getmtime(sx)
                                    if datetime.datetime.now() - deltime < trashdelay:
                                        remove = False
                                if remove:
                                    if fxtype == Filesystem.Link:
                                        fs.removelink(fx)
                                    else:
                                        fs.removefile(fx)
                                    try:
                                        fs.removefile(sx)
                                    except Exception:
                                        pass
                                    machine.logremove(fs, px, runtime, verb="removed from trashbin",
                                                      comment="on "+fs.name)
                                    dname = os.path.dirname(fx)
                                    while len(dname) > len("/.parsley.control/deleted_files/"):
                                        if len(fs.listdir(dname)) == 0:
                                            fs.removedir(dname)
                                        dname = os.path.dirname(dname)

                def helper2(fpath, spath):
                    if fs.exists(spath):
                        for x in fs.listdir(spath):
                            fx = fpath + "/" + x
                            sx = spath + "/" + x
                            fxtype = fs.getftype(fx)
                            if fxtype == Filesystem.Directory:
                                helper2(fx, sx)
                            elif not fs.exists(fx) and fs.getftype(sx) == Filesystem.File:
                                fs.removefile(sx)
                        if len(fs.listdir(spath)) == 0:
                            fs.removedir(spath)

                helper1("", "/.parsley.control/deleted_files", "/.parsley.control/deleted_files_states")
                helper2("/.parsley.control/deleted_files", "/.parsley.control/deleted_files_states")
        return _x

    def hook(self, machine, isglobal, fss):
        RemoveOrphanedDirs.hook(self, machine, isglobal, fss)
        for fs in fss:
            machine.addhook(fs, SyncHooks.onendupdatedir, 50000, CleanupTrashBin._cleanup_trashbin(fs, machine, self.trashdelay))


## Default removal strategy without a trashbin.
class DefaultRemove(Aspect):
    def __init__(self):
        RemoveOrphanedDirs.__init__(self)
        CleanupTrashBin.__init__(self)

    ## Removes the file or link from the filesystem.
    @staticmethod
    def _removefile(fs, machine):
        def _x(srcfs, path, runtime):
            ftype = fs.getftype(path)
            if ftype == Filesystem.File:
                fs.removefile(path)
            elif ftype == Filesystem.Link:
                fs.removelink(path)
            machine.filelists[fs].removefile(path)
            machine.logremove(fs, path, runtime, comment="on "+fs.name)
            runtime.changed_flag = True
        return _x

    def hook(self, machine, isglobal, fss):
        RemoveOrphanedDirs.hook(self, machine, isglobal, fss)
        CleanupTrashBin.hook(self, machine, isglobal, fss)
        for fs in fss:
            machine.addhook(fs, SyncHooks.onremovefile, 50000, DefaultRemove._removefile(fs, machine))
            machine.addhook(fs, SyncHooks.onremovelink, 50000, DefaultRemove._removefile(fs, machine))


## Removal strategy with a trashbin.
class TrashRemove(Aspect):
    def __init__(self, trashdelay=datetime.timedelta(days=7)):
        RemoveOrphanedDirs.__init__(self)
        CleanupTrashBin.__init__(self, trashdelay=trashdelay)

    ## Moves a file or link to the trash bin.
    @staticmethod
    def _movetotrashbin(fs, machine):
        def _x(srcfs, path, runtime):
            trashedpath = os.path.abspath("/.parsley.control/deleted_files/" + path)
            i = 0
            drelpath = path
            _trashedpath = trashedpath
            while fs.exists(trashedpath):
                drelpath = path + ".." + str(i)
                trashedpath = _trashedpath + ".." + str(i)
                i += 1
            statespath = os.path.abspath("/.parsley.control/deleted_files_states/" + drelpath)
            fs.createdirs(os.path.dirname(trashedpath))
            fs.move(path, trashedpath)
            fs.createdirs(os.path.dirname(statespath))
            fs.writetofile(statespath, path)
            machine.filelists[fs].removefile(path)
            machine.logremove(fs, path, runtime, verb="trashed", comment="on "+fs.name, severity=Severity.MOREIMPORTANT)
            runtime.changed_flag = True
        return _x

    def hook(self, machine, isglobal, fss):
        RemoveOrphanedDirs.hook(self, machine, isglobal, fss)
        CleanupTrashBin.hook(self, machine, isglobal, fss)
        for fs in fss:
            machine.addhook(fs, SyncHooks.onremovefile, 50000, TrashRemove._movetotrashbin(fs, machine))
            machine.addhook(fs, SyncHooks.onremovelink, 50000, TrashRemove._movetotrashbin(fs, machine))

