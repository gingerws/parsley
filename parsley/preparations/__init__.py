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

##@package parsley.preparations
## Pluggable initialization steps which can be wrapped around task executions by adding them to the task configuration.
## Implement custom preparations by subclassing parsley.preparations.Preparation.

import datetime

## Abstract base class for all logic, which does preparation work for the actual synchronization run
## in advance or afterwards (like mounting filesystems, cleaning up stuff).
class Preparation:
    def __init__(self, *, tries=3):
        self.tries = tries

    ## Runs the preparation work.
    def enable(self):
        pass

    ## Undo the preparation after the synchronizaion (like unmounting).
    def disable(self):
        pass

    ## Checks if the preparation is successfully done or not.
    ## The parsley engine will check the state with this method at certain times and decide what to do
    ## depending on the state and the return values of ensuredisabledbefore, ensuredisabledafter and
    ## ensureenabled.
    def getstate(self):
        pass

    ## Defines if this preparation is required to be disabled before the synchronization begins.
    ## For example, it is an error situation if a certain mountpoint is already mounted before this preparation
    ## has mounted it.
    def ensuredisabledbefore(self):
        return True

    ## Defines if this preparation is required to be disabled after the synchronization ended.
    ## For example, it is an error situation if a certain mountpoint is mounted even after this preparation
    ## has unmounted it.
    def ensuredisabledafter(self):
        return True

    ## Defines if this preparation is required to be successful for the ongoing process of synchronization.
    ## For example, a preparation which just does some uncritical cleanup, should not stop the complete
    ## synchronization if it fails.
    def ensureenabled(self):
        return True
