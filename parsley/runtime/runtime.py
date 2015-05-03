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

##@package parsley.runtime.runtime
## The implementation for some parsley core features

from parsley.logger.severity import Severity
from parsley.runtime.warnhelper import WarnHelper


## Runtime data for synchronization runs used by the parsley engine and some higher layers. Used by the
## synchronization implementations for logging, for communicating success values and for retrieving/setting some
## environment values. Typically, there is one instance for each engine run (which can do multiple synchronizations).
class RuntimeData:

    def __init__(self, datadir, loggers):
        self.retval = 0
        self.mydir = datadir
        self.loggers = loggers
        self.warner = WarnHelper(self)
        self.taskdata = {}
        self.currentsync = None
        self.lastsyncsuccess = None

    ## This is the log method which is actually used by clients.
    ## @param subject The name of the subject, e.g. a file name (arbitrary string).
    ## @param verb A description what happened with the subject, e.g. 'deleted' or 'created' (arbitrary string).
    ## @param comment A description following after the verb (arbitrary string).
    ## @param severity A parsley.logger.severity.Severity describes how important this message is. This value
    ##                 decides if the message will be really logged.
    ## @param symbol One character which describes the kind of log message (arbitrary string).
    def log(self, *, subject="", verb="", comment="", severity=Severity.INFO, symbol=""):
        for logger in self.loggers:
            logger.log(self.currentsync.fullname, subject, verb, comment, severity, symbol)

    ## Signals the logger to finish logging now and to submit all it's contents.
    def shutdown(self):
        for logger in self.loggers:
            logger.flush()
