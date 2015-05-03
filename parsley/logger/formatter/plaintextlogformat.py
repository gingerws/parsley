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

import datetime
from parsley.logger.formatter import Logformat


class PlaintextLogformat(Logformat):

    def __init__(self, maxlen=80, color=None):
        Logformat.__init__(self)
        self.maxlen = maxlen
        self.color = color

    def header(self):
        return ""

    def log(self, sync, subject, verb, comment, severity, symbol):
        result = ""
        sevstring = (("." * severity).replace("..", ":") + "   ")[0:3]
        pr = datetime.datetime.now().strftime("%Y%m%d %H%M%S") \
             + " " + sevstring + " " + (symbol + " ")[0] + " "
        fullmsg = sync + " " + subject + ("" if verb == "" else (" " + verb)) + \
                  ("" if comment == "" else (" " + comment))
        for line in fullmsg.split("\n"):
            while len(line) > 0:
                l = self.maxlen - len(pr)
                if len(line) > l:
                    sp = line.rfind(" ", 0, l)
                    if sp > -1:
                        l = sp
                _line = line[0:l].strip()
                line = line[l:].strip()
                result += (pr if result == "" else " " * len(pr)) + _line + "\n"
        if self.color:
            result = "\033[9{0}m".format(self.color) + result + "\033[0m"
        return result

    def footer(self):
        return ""
