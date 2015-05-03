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
from parsley.logger.loggerout import Loggerout
from parsley.tools.common import call


class ExternalProgramLoggerout(Loggerout):

    def __init__(self, *, cmdline):
        Loggerout.__init__(self)
        self.cmdline = cmdline
        self.cont = ""

    def log(self, content):
        self.cont += content

    def flush(self, wasused):
        if wasused:
            cmdline = []
            for x in self.cmdline:
                if x.endswith("{}"):
                    t = None
                    i = 0
                    while t is None or os.path.exists(t):
                        t = "/tmp/parsley.{0}".format(i)
                        i += 1
                    with open(t, "w") as f:
                        f.write(self.cont)
                    cmdline.append(x[:-2] + t)
                elif x.endswith("[]"):
                    cmdline.append(x[:-2] + self.cont)
                else:
                    cmdline.append(x)
            call(cmdline)
