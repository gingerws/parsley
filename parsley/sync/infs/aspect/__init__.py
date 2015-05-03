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

##@package parsley.sync.infs.aspect
## Aspect implementations control the behavior of parsley.sync.infs.InFsSync configurations. Each feature should be
## encapsulated as one subclass of parsley.sync.infs.aspect.Aspect which hooks some event handlers into the processing
## chain.

## Abstract base class for behavior implementations which build the actual behavior of a
## parsley.sync.infs.InFsSync synchronization implementation.
class Aspect:
    def __init__(self):
        pass

    ## Request to hook program logic into certain events in 'machine'.
    ## @param machine the parsley.sync.infs.syncmachine.SyncMachine instance.
    def hook(self, machine, isglobal, fss):
        pass


