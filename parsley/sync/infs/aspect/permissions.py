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
import pwd
import grp
from parsley.sync.infs import ActionControl, Filesystem
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Applies the specified file system permissions to all entries processed by parsley.
class ApplyPermissions(Aspect):

    def __init__(self, user, group, fileaddperms, filesubtractperms, diraddperms, dirsubtractperms):
        Aspect.__init__(self)
        self.user = user
        self.group = group
        if isinstance(user, str):
            self.user = pwd.getpwnam(user).pw_uid
        if isinstance(group, str):
            self.group = grp.getgrnam(group).gr_gid
        self.fileaddperms = fileaddperms
        self.diraddperms = diraddperms
        self.filesubtractperms = filesubtractperms
        self.dirsubtractperms = dirsubtractperms

    @staticmethod
    def _setperms(path, uid, gid, addperms, subtractperms):
        perms = os.stat(path).st_mode
        perms = (perms & ~subtractperms) | addperms
        os.chmod(path, perms)
        os.chown(path, uid, gid)

    ## Sets the file permissions of a file entry to what is configured in the aspect.
    @staticmethod
    def _set_file_permissions(fs, user, group, fileaddperms, filesubtractperms):
        def _x(srcfs, path, runtime):
            if fs.getftype(path) == Filesystem.File:
                ApplyPermissions._setperms(fs.getfulllocalpath(path), user, group,
                                           fileaddperms, filesubtractperms)
        return _x

    ## Sets the file permissions of a dir entry to what is configured in the aspect.
    @staticmethod
    def _set_dir_permissions(fs, user, group, diraddperms, dirsubtractperms):
        def _x(path, runtime):
            if fs.getftype(path) == Filesystem.Directory:
                ApplyPermissions._setperms(fs.getfulllocalpath(path), user, group,
                                           diraddperms, dirsubtractperms)
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onupdatefile, 80000, ApplyPermissions._set_file_permissions(fs, self.user, self.group, self.fileaddperms, self.filesubtractperms))
            machine.addhook(fs, SyncHooks.onendupdatedir, 10000, ApplyPermissions._set_dir_permissions(fs, self.user, self.group, self.diraddperms, self.dirsubtractperms))
