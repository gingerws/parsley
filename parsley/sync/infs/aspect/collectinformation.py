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

from parsley.sync.infs import Filesystem
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Used for populating the machine.filelists lists.
class CollectInformation(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Collects information (type, size, ...) for this entry from the filesystem and stores it to machine.filelists.
    @staticmethod
    def _collectinfo(fs, machine):
        def _x(path, runtime):
            ftype = fs.getftype(path)
            if ftype:
                if ftype == Filesystem.Link:
                    param = fs.getlinktarget(path)
                    size = None
                    mtime = None
                else:
                    mtime = fs.getmtime(path)
                    size = fs.getsize(path)
                    param = None
                machine.filelists[fs].foundfile(path, ftype, size, mtime, param)
        return _x


    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onelectmaster, 20000, CollectInformation._collectinfo(fs, machine))
