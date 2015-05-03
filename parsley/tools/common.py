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

##@package parsley.tools.common
## Tools for very common jobs.

import subprocess


## Executes an external process and returns a tuple of returnvalue and program output.
def call(*cmdline, shell=False, decode=True, errorstring=None):
    ret = 0
    try:
        if len(cmdline) == 1:
            cmdline = cmdline[0]
        r = subprocess.check_output(cmdline, stderr=subprocess.STDOUT, shell=shell)
    except subprocess.CalledProcessError as err:
        ret = err.returncode
        r = err.output
    if ret != 0 and errorstring:
        raise Exception(errorstring + ": " + r.decode())
    rd = r.decode() if decode else r
    return rd if errorstring else (ret, rd)

