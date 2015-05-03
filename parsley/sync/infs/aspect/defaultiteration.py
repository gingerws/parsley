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

from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Lists child elements via the filesystem.
class DefaultIteration(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Adds all the child entries to the list (as returned by underlying the filesystem).
    @staticmethod
    def _getlist_from_filesystem(fs):
        def _x(path, ret, runtime):
            if fs.exists(path):
                ret.update(fs.listdir(path))
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onlistdir, 50000, DefaultIteration._getlist_from_filesystem(fs))
