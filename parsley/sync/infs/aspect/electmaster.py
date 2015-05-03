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

import time
from parsley.sync.infs import Filesystem
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Elects a master file by mtime. Default master election strategy for files.
class ElectMasterFileByMtime(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Returns the mtime of this entry as election key.
    @staticmethod
    def _electbymtime(fs, machine):
        def _x(path, runtime):
            if machine.filelists[fs].exists(path):
                ftype = machine.filelists[fs].getftype(path)
                if ftype != Filesystem.Link:
                    mtime = machine.filelists[fs].getmtime(path)
                    return time.mktime(mtime.timetuple())
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onelectmaster, 40000, ElectMasterFileByMtime._electbymtime(fs, machine))


## Elects a master link by changes in history. Default master election strategy for links.
class ElectMasterLinkByTargetHistory(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Returns 0 if the link remained unchanged since last sync, or 1 otherwise as election key.
    @staticmethod
    def _electbychangedflag(fs, machine):
        def _x(path, runtime):
            paramd = machine.filelists[fs].getparam(path)
            paramdl = machine.lastfilelists[fs].getparam(path)
            return 0 if (paramdl == paramd) else 1
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onelectmaster, 50000, ElectMasterLinkByTargetHistory._electbychangedflag(fs, machine))
