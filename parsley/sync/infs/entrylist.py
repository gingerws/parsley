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

##@package parsley.sync.infs.entrylist
## Internal in-memory list of entries for one filesystem with (de-)serialization features.

import os
import pickle


class EntryList:
    def __init__(self):
        self.d = {}

    def foundfile(self, path, ftype, size, mtime, param):
        self.d[path] = (path, ftype, size, mtime, param)

    def updatefile(self, path, ftype, size, mtime, param):
        self.foundfile(path, ftype, size, mtime, param)

    def removefile(self, path):
        try:
            del self.d[path]
        except KeyError: pass

    def savetofile(self, f):
        with open(f, 'wb') as ff:
            pickle.dump(list(self.d.values()), ff)

    def readfromfile(self, f):
        self.d = {}
        if os.path.exists(f):
            with open(f, 'rb') as ff:
                _oldlst = pickle.load(ff)
            for v in _oldlst:
                self.d[v[0]] = v

    def exists(self, path):
        return (path in self.d)

    def getftype(self, path):
        return self.d[path][1] if (path in self.d) else None

    def getsize(self, path):
        return self.d[path][2] if (path in self.d) else None

    def getmtime(self, path):
        return self.d[path][3] if (path in self.d) else None

    def getparam(self, path):
        return self.d[path][4] if (path in self.d) else None


class CombinedEntryList:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def foundfile(self, path, ftype, size, mtime, param):
        self.first.foundfile(path, ftype, size, mtime, param)

    def updatefile(self, path, ftype, size, mtime, param):
        self.first.updatefile(path, ftype, size, mtime, param)
        self.second.updatefile(path, ftype, size, mtime, param)

    def removefile(self, path):
        self.first.removefile(path)
        self.second.removefile(path)

    def exists(self, path):
        return self.first.exists(path)

    def getftype(self, path):
        return self.first.getftype(path)

    def getsize(self, path):
        return self.first.getsize(path)

    def getmtime(self, path):
        return self.first.getmtime(path)

    def getparam(self, path):
        return self.first.getparam(path)
