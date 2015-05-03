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

import os
import time
from parsley.preparations import Preparation
from parsley.tools.common import call


## Mounts filesystems to a mountpoint.
class MountPreparation(Preparation):
    def __init__(self, *, src, tgt, opts=[], **kwa):
        Preparation.__init__(self, **kwa)
        self.src = src
        self.tgt = tgt
        self.opts = opts

    @staticmethod
    def _checkmountpointempty(tgt):
        if len(os.listdir(tgt)) > 0:
            raise Exception("The mountpoint {tgt} is not empty before mounting.".format(tgt=tgt))

    def enable(self, runtime):
        if not os.path.exists(self.tgt):
            os.makedirs(self.tgt)
        MountPreparation._checkmountpointempty(self.tgt)
        (ret, r) = call("sudo", "mount", self.src, self.tgt, *self.opts)
        if ret != 0:
            raise Exception(self.src + " not mounted: " + r)
        time.sleep(1)

    def disable(self, runtime):
        call("sync")
        call("sync")
        (ret, r) = call("sudo", "umount", self.tgt)
        if ret != 0:
            raise Exception(self.src + " not unmounted: " + r)
        time.sleep(1)

    def getstate(self, runtime):
        (ret, r) = call(["mount"])
        if ret != 0:
            raise Exception("list mounts error: " + r)
        return r.find(" " + self.tgt + " ") > -1


