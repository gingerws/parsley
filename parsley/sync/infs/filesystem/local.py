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
import shutil
import datetime
import time
from parsley.sync.infs import Filesystem
try:
    import xattr
except Exception:
    pass


class LocalFilesystem(Filesystem):
    def __str__(self):
        return "[local {path}]".format(path=self.rootpath)

    def __init__(self, *aspects, name, path):
        Filesystem.__init__(self, *aspects, name=name)
        self.rootpath = path
        self._enable_workaround_mtimeOnlyInt = False

    def listdir(self, path):
        fpath = self.getfulllocalpath(path)
        ret = os.listdir(fpath)
        return ret

    def copyfile(self, srcpath, dstpath, expecteddestmtime=None):
        path = None
        i = 1
        while path is None or os.path.exists(path):
            path = "%s/.parsley.control/deleted_files/_parsley_currenttransfer.%d" % (self.rootpath, i)
            i += 1
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        mt = os.stat(srcpath).st_mtime
        if self._enable_workaround_mtimeOnlyInt:
            mt = int(mt)
        if self._enable_workaround_mtimeOnlyInt and (time.time()-mt < 60):  # just be sure that we would detect dirty copies
            time.sleep(1.1)
        shutil.copy2(srcpath, path)
        if self._enable_workaround_mtimeOnlyInt and mt != int(os.stat(srcpath).st_mtime):  # more dirty copy detection
            return None, None
        msize = os.stat(path).st_size
        fulldpath = os.path.abspath(self.rootpath + "/" + dstpath)
        if not os.path.isdir(os.path.dirname(fulldpath)):
            os.makedirs(os.path.dirname(fulldpath))
        os.utime(path, (mt, mt))
        if expecteddestmtime and os.path.exists(fulldpath):
            newmtime = os.stat(fulldpath).st_mtime
            if self._enable_workaround_mtimeOnlyInt:
                newmtime = int(newmtime)
            if expecteddestmtime != datetime.datetime.fromtimestamp(newmtime):
                return None, None
        os.rename(path, fulldpath)
        return datetime.datetime.fromtimestamp(mt), msize

    def removefile(self, path):
        fpath = self.getfulllocalpath(path)
        os.unlink(fpath)

    def createdirs(self, path):
        fpath = self.getfulllocalpath(path)
        if not os.path.exists(fpath):
            os.makedirs(fpath)

    def removedir(self, path, recursive=False):
        fpath = self.getfulllocalpath(path)
        if recursive:
            shutil.rmtree(fpath)
        else:
            os.rmdir(fpath)

    def createlink(self, srcpath, dstpath):
        fdst = self.getfulllocalpath(dstpath)
        os.symlink(srcpath, fdst)

    def removelink(self, path):
        fpath = self.getfulllocalpath(path)
        os.unlink(fpath)

    def move(self, path, dst):
        fpath = self.getfulllocalpath(path)
        fdst = self.getfulllocalpath(dst)
        os.rename(fpath, fdst)

    def getftype(self, path):
        fpath = self.getfulllocalpath(path)
        if os.path.islink(fpath):
            return Filesystem.Link
        elif os.path.isdir(fpath):
            return Filesystem.Directory
        elif os.path.isfile(fpath):
            return Filesystem.File
        else:
            return None

    def exists(self, path):
        fpath = self.getfulllocalpath(path)
        return os.path.exists(fpath) or os.path.islink(fpath)

    def getsize(self, path):
        fpath = self.getfulllocalpath(path)
        return os.stat(fpath).st_size

    def getmtime(self, path):
        fpath = self.getfulllocalpath(path)
        mt = os.stat(fpath).st_mtime
        if self._enable_workaround_mtimeOnlyInt:
            mt = int(mt)
        return datetime.datetime.fromtimestamp(mt)

    def getlinktarget(self, path):
        fpath = self.getfulllocalpath(path)
        return os.readlink(fpath)

    def getfulllocalpath(self, path):
        return os.path.abspath(self.rootpath + "/" + path)

    def writetofile(self, path, content):
        fpath = self.getfulllocalpath(path)
        with open(fpath, "w") as f:
            f.write(content)

    def listxattrkeys(self, path):
        fpath = self.getfulllocalpath(path)
        res = xattr.list(fpath)
        return [x.decode("utf-8") for x in res]

    def getxattrvalue(self, path, key):
        fpath = self.getfulllocalpath(path)
        return xattr.get(fpath, key).decode("utf-8")

    def setxattrvalue(self, path, key, value):
        fpath = self.getfulllocalpath(path)
        xattr.set(fpath, key, value)

    def unsetxattrvalue(self, path, key):
        fpath = self.getfulllocalpath(path)
        xattr.remove(fpath, key)

    def initialize(self, infssync, runtime):
        if not os.path.isdir(self.rootpath):
            raise Exception("the path '{path}' for '{fs}' does not exist.".format(path=self.rootpath, fs=self.name))
