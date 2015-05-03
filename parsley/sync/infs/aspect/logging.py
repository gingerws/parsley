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


## Switchable logging by situation.
class Logging(Aspect):
    def __init__(self, *, logcreate=False, logremove=False, logupdate=False, logproblem=True):
        Aspect.__init__(self)
        self.logcreate = logcreate
        self.logremove = logremove
        self.logupdate = logupdate
        self.logproblem = logproblem

    ## Logs an entry update (only hooked if this is activated in aspect configuration).
    @staticmethod
    def _logupdate():
        def _x(subject, runtime, verb, comment, symbol, severity):
            runtime.log(subject=subject, verb=verb, comment=comment, symbol=symbol, severity=severity)
        return _x

    ## Logs an entry removal (only hooked if this is activated in aspect configuration).
    @staticmethod
    def _logremove():
        def _x(subject, runtime, verb, comment, symbol, severity):
            runtime.log(subject=subject, verb=verb, comment=comment, symbol=symbol, severity=severity)
        return _x

    ## Logs an entry creation (only hooked if this is activated in aspect configuration).
    @staticmethod
    def _logcreate():
        def _x(subject, runtime, verb, comment, symbol, severity):
            runtime.log(subject=subject, verb=verb, comment=comment, symbol=symbol, severity=severity)
        return _x

    ## Logs a problem (only hooked if this is activated in aspect configuration).
    @staticmethod
    def _logproblem():
        def _x(subject, runtime, verb, comment, symbol, severity):
            runtime.log(subject=subject, verb=verb, comment=comment, symbol=symbol, severity=severity)
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            if self.logcreate:
                machine.addhook(fs, SyncHooks.onlogcreate, 50000, Logging._logcreate())
            if self.logremove:
                machine.addhook(fs, SyncHooks.onlogremove, 50000, Logging._logremove())
            if self.logupdate:
                machine.addhook(fs, SyncHooks.onlogupdate, 50000, Logging._logupdate())
            if self.logproblem:
                machine.addhook(fs, SyncHooks.onlogproblem, 50000, Logging._logproblem())
