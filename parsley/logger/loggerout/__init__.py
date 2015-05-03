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

##@package parsley.logger.loggerout
## Output destinations for log message strings.

##@pure
## Abstract base class for log message sinks.
class Loggerout:

    def __init__(self):
        pass

    ## Writes the rendered content to the logger (can be log messages, html header or footer, ...).
    def log(self, content):
        pass

    ## Commits the log content to the sink and closes the logger.
    ## @param wasused if there was any useful logged message (instead of just headers and footers).
    def flush(self, wasused):
        pass
