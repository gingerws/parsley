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

##@package parsley.logger.formatter
## Transforming log message structures to strings.

## Abstract base class for log message formatters (html, plain, ...)
class Logformat:

    def __init__(self):
        pass

    ## Returns a header string for the log output (like an html header).
    def header(self):
        return ""

    ## Renders the information for one log message into a formatted string (plaintext, html, ...).
    def log(self, sync, subject, verb, comment, severity, symbol):
        return ""

    ## Returns a footer string for the log output (like an html footer).
    def footer(self):
        return ""

