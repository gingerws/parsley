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

from parsley.sync.infs import ElectionControl
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Filters out directories which should be excluded from syncing. It works by providing a path acceptor function.
class ApplyPathAcceptor(Aspect):
    def __init__(self, acceptor, _dontthrowexceptiononnonglobalusage=False):
        Aspect.__init__(self)
        self._dontthrowexceptiononnonglobalusage = _dontthrowexceptiononnonglobalusage
        self.acceptor = acceptor

    ## Skips this entry if it is rejected by the path acceptor.
    @staticmethod
    def _skip_by_pathacceptor(acceptor):
        def _x(path, runtime):
            if not acceptor(path):
                return ElectionControl.SKIP
        return _x

    def hook(self, machine, isglobal, fss):
        if (not isglobal) and (not self._dontthrowexceptiononnonglobalusage):
            raise Exception("ApplyPathAcceptor can only be used globally")
        for fs in fss:
            machine.addhook(fs, SyncHooks.onelectmaster, 10000, ApplyPathAcceptor._skip_by_pathacceptor(self.acceptor))
