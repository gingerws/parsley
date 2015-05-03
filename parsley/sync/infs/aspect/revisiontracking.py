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
from parsley.sync.infs import Filesystem
from parsley.sync.infs.syncmachine import SyncHooks
from parsley.sync.infs.aspect import Aspect


## Keeps all versions of all files which parsley has seen into a revision storage in the control directory.
class RevisionTracking(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    @staticmethod
    def _updatefile_helper(_fs, path, machine):
        if machine.filelists[_fs].getftype(path) == Filesystem.File:
            mtime = machine.filelists[_fs].getmtime(path).strftime("%Y-%m-%d %H:%M:%S.%f")
            rcpath = "/.parsley.control/content_revisions/{path}/{mtime}".format(
                path=path, mtime=mtime)
            rcpath = os.path.abspath(rcpath)
            if not _fs.exists(rcpath):
                _fs.copyfile(_fs.getfulllocalpath(path), rcpath)

    ## Checks if the version with the current mtime of this entry is already stored in the version history, and if not, do so.
    @staticmethod
    def _store_current_version1(fs, machine):
        def _x(srcfs, path, runtime):
            return RevisionTracking._updatefile_helper(fs, path, machine)
        return _x

    ## Checks if the version with the current mtime of this entry is already stored in the version history, and if not, do so.
    @staticmethod
    def _store_current_version2(fs, machine):
        def _x(path, runtime):
            return RevisionTracking._updatefile_helper(fs, path, machine)
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onupdatefile, 80000, RevisionTracking._store_current_version1(fs, machine))
            machine.addhook(fs, SyncHooks.onelectmaster, 30000, RevisionTracking._store_current_version2(fs, machine))
