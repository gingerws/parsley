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

##@package parsley.logger.logger
## High level interface.

from parsley.logger.severity import Severity


## Used by higher layers for logging messages.
## Contains a parsley.logger.formatter.Logformat and a parsley.logger.loggerout.Loggerout and defines which severity
## span should actually be logged.
class Logger:
    def __init__(self, *, formatter, loggerout, minseverity=Severity.INFO, maxseverity=Severity.ERROR):
        self.loggerout = loggerout
        self.formatter = formatter
        self.minseverity = minseverity
        self.maxseverity = maxseverity
        content = self.formatter.header()
        self.loggerout.log(content)
        self.used = False

    ## Logs a message.
    ## @param sync The name of the synchronization task which is presented as the source (arbitrary string).
    def log(self, sync, subject, verb, comment, severity, symbol):
        if self.minseverity <= severity <= self.maxseverity:
            content = self.formatter.log(sync, subject, verb, comment, severity, symbol)
            self.loggerout.log(content)
            self.used = True

    ## Closes the logger and commits the content.
    def flush(self):
        content = self.formatter.footer()
        self.loggerout.log(content)
        self.loggerout.flush(self.used)

