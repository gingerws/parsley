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

##@package parsley.runtime.warnhelper
## Helps invoking warning messages after some time of sync problems.

import datetime
import os
from parsley.logger.severity import Severity


## Used internally for logging warnings when a synchronization did not run successfully since a certain
## timespan. It stores timestamps on the filesystem for this functionality.
class WarnHelper:

    def __init__(self, runtime):
        self.r = runtime
        self.syncs = None

    ## Sets the list of sync tasks for processing.
    def setscope(self, syncs):
        self.syncs = syncs

    ## Marks a sync task as successfully executed.
    def successfulcall(self, sync):
        n = self.r.mydir + "/lastsuccess.%s" % (sync.fullname,)
        now = (datetime.datetime.now() - datetime.datetime(2000, 1, 1)).total_seconds()
        with open(n, "w") as f:
            f.write(str(int(now)) + "\n")

    ## Determines if a sync task should be skipped now.
    def shall_skip(self, sync):
        n = self.r.mydir + "/lastsuccess.%s" % (sync.fullname,)
        if os.path.isfile(n):
            with open(n, "r") as f:
                succcnt = "".join(f.readlines())
            if not succcnt.startswith(" "):
                lastsucc = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=int(succcnt.strip()))
                return datetime.datetime.now() - lastsucc < sync.interval
        return False

    ## Signals that a task execution was scheduled for now and the process is over. This happens for successful
    ## and for failed executions and triggers a warning notification in certain situations.
    def end(self):
        for sync in self.syncs:
            self.r.currentsync = sync
            n = self.r.mydir + "/lastsuccess.%s" % (sync.fullname,)
            m = self.r.mydir + "/lastwarned.%s" % (sync.fullname,)
            if os.path.isfile(n):
                with open(n, "r") as f:
                    lastsucc = datetime.datetime(2000, 1, 1) + \
                        datetime.timedelta(seconds=int("".join(f.readlines()).strip()))
                escalationfactor = max(1, sync.warn_escalationfactor * ((datetime.datetime.now() - lastsucc
                                       - sync.warn_after).total_seconds() / (60 * 60 * 24.)))
            else:
                lastsucc = datetime.datetime(1999, 1, 1)
                escalationfactor = 1
            if datetime.datetime.now() - lastsucc > sync.warn_after:
                if os.path.isfile(m):
                    with open(m, "r") as f:
                        lastwarned = datetime.datetime(2000, 1, 1) + \
                            datetime.timedelta(seconds=int("".join(f.readlines()).strip()))
                else:
                    lastwarned = datetime.datetime(2000, 1, 1)
                if datetime.datetime.now() - lastwarned > sync.warn_interval / escalationfactor:
                    i = datetime.datetime.now() - lastsucc
                    if i.total_seconds() < 60:
                        d = str(int(i.total_seconds()))
                        d += " second" + ("s" if (d != "1") else "")
                    elif i.total_seconds() < 60 * 60:
                        d = str(int(i.total_seconds() / 60))
                        d += " minute" + ("s" if (d != "1") else "")
                    elif i.total_seconds() < 24 * 60 * 60:
                        d = str(int(i.total_seconds() / (60 * 60)))
                        d += " hour" + ("s" if (d != "1") else "")
                    elif i.days < 30:
                        d = str(int(i.days))
                        d += " day" + ("s" if (d != "1") else "")
                    elif i.days < 365:
                        d = str(int(i.days / 30))
                        d += " month" + ("s" if (d != "1") else "")
                    else:
                        d = str(int(i.days / 365))
                        d += " year" + ("s" if (d != "1") else "")
                    self.r.log(subject=sync.fullname, verb="not exec'ed since " + d, severity=Severity.ERROR)
                    now = (datetime.datetime.now() - datetime.datetime(2000, 1, 1)).total_seconds()
                    with open(m, "w") as f:
                        f.write(str(int(now)) + "\n")
