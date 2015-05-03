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

from parsley.sync.infs import ConflictResolution
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


## Handles file conflicts between two filesystems (file vs directory, for example).
class DetectTypeConflicts(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Skips this entry as conflict resolution strategy (with logged warning).
    @staticmethod
    def _log_and_skip(fs, machine):
        def _x(path, m, s, runtime):
            machine.logproblem(fs, path, runtime, verb=" has conflicting file types")
            return ConflictResolution.SKIP
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.ontypeconflictmaster, 50000, DetectTypeConflicts._log_and_skip(fs, machine))
