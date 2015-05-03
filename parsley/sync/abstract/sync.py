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

from datetime import timedelta


## Abstract base class for a synchronization implementation.
## @param cfgs some configuration structures. they depend on the implementation class what makes sense here.
## @param name the name for this synchronization
## @param host the host name associated with this synchronization
## @param interval the synchronization interval (the engine will skip this synchronization, if the last
##                 successful run is not at least this interval ago.
## @param warn_after the interval after which a warning is logged when no successful run took place.
## @param warn_interval the interval for subsequent warnings when no successful run took place.
## @param warn_escalationfactor a number which controls how fast the warning interval shrinks.
## @param preparations a list of parsley.preparations.Preparation describing additional post/pre
##                     execution tasks
class Sync:
    def __init__(self, *cfgs, name,
                 host="localhost",
                 interval=timedelta(minutes=30),
                 warn_after=timedelta(days=7),
                 warn_interval=timedelta(days=7),
                 warn_escalationfactor=1,
                 preparations=None):
        self.host = host
        self.name = name
        self.cfgs = cfgs
        self.fullname = host + "~" + name
        self.interval = interval
        self.warn_after = warn_after
        self.warn_interval = warn_interval
        self.warn_escalationfactor = warn_escalationfactor
        self.preparations = preparations if preparations else []

    def initialize(self, runtime):
        pass

    def shutdown(self, runtime):
        pass

    def execute(self, runtime):
        pass
