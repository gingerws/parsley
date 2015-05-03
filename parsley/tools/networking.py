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

##@package parsley.tools.networking
## Parsley networking features

import os
import socket


## Provides functionality for using parsley through an ssh remote port forwarding tunnel.
def translate_parsley_portforwarding(machine, port, runtime):
    tfile = runtime.mydir + "/tcp_forward_" + machine + "." + str(port)
    if os.path.isfile(tfile):
        with open(tfile, "r") as f:
            locport = int("".join(f.readlines()))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", locport))
        portopen = result == 0
        sock.close()
        if portopen:
            return "localhost", str(locport)
    return machine, str(port)
