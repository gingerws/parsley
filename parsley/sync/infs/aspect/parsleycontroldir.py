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

from parsley.sync.infs.syncmachine import SyncHooks
from parsley.sync.infs.aspect import Aspect


## Takes care that the parsley control directory exists.
class CreateParsleyControlDirectory(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Ensures that the parsley control dir `.parsley.control` exists (only executed when in the root path).
    @staticmethod
    def _create_controldir(fs):
        def _x(path, runtime):
            if path == "":
                fs.createdirs("/.parsley.control")
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onbeginupdatedir, 40000, CreateParsleyControlDirectory._create_controldir(fs))
