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
from parsley.logger.severity import Severity
from parsley.sync.infs.syncmachine import SyncHooks
from parsley.sync.infs.aspect import Aspect


## Handles filesystems with mtime precision only on level of seconds.
class DetectFilesystemMtimePrecision(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    ## Detects if the filesystem has time a precision on millisecond level and otherwise enables a workaround in
    ## *all* filesystems.
    @staticmethod
    def _enable_workaround_if_needed(fs, machine):
        def _x(path, runtime):
            if path == "":
                p = "/.parsley.control/test_mtime_precision"
                floatseen = False
                for i in range(6):
                    fs.writetofile(p, "")
                    x = fs.getmtime(p)
                    fs.removefile(p)
                    time.sleep(0.1337)
                    if i % 3 == 0: time.sleep(0.4)
                    if x.microsecond > 0:
                        floatseen = True
                        break
                if not floatseen:
                    for _fs in machine.filesystems:
                        if not _fs._enable_workaround_mtimeOnlyInt:
                            runtime.log(subject="Enabled workaround", comment="'mtime only int'",
                                        severity=Severity.DEBUG)
                            _fs._enable_workaround_mtimeOnlyInt = True
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onbeginupdatedir, 60000, DetectFilesystemMtimePrecision._enable_workaround_if_needed(fs, machine))
