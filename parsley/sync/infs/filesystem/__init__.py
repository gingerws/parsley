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

##@package parsley.sync.infs.filesystem
## Filesystem implementations for use with parsley.sync.infs.InFsSync.

class Filesystem:
    File = "FILE"
    Link = "LINK"
    Directory = "DIRECTORY"

    def __init__(self, *aspects, name):
        self.aspects = aspects
        self.name = name

    def listdir(self, path):
        pass

    def copyfile(self, srcpath, dstpath, expecteddestmtime=None):
        pass

    def removefile(self, path):
        pass

    def createdirs(self, path):
        pass

    def removedir(self, path, recursive=False):
        pass

    def createlink(self, srcpath, dstpath):
        pass

    def removelink(self, path):
        pass

    def move(self, path, dst):
        pass

    def getftype(self, path):
        pass

    def exists(self, path):
        pass

    def getsize(self, path):
        pass

    def getmtime(self, path):
        pass

    def getlinktarget(self, path):
        pass

    def getfulllocalpath(self, path):
        pass

    def writetofile(self, path, content):
        pass

    def listxattrkeys(self, path):
        pass

    def getxattrvalue(self, path, key):
        pass

    def setxattrvalue(self, path, key, value):
        pass

    def unsetxattrvalue(self, path, key):
        pass

    def initialize(self, infssync, runtime):
        pass

    def shutdown(self, infssync, runtime):
        pass