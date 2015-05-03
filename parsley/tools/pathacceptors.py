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

##@package parsley.tools.pathacceptors
## Default implementation for path acceptors as e.g. used in
## parsley.sync.infs.aspect.applypathacceptor.ApplyPathAcceptor.

import os


## A path acceptor which skips file names with some known 'backup pattern', like ending with `~`.
def defaultpathacceptor(p):
    bn = os.path.basename(p)
    if bn.endswith("~"):
        return False
    if bn.endswith(".kate-swp"):
        return False
    if bn.startswith(".#"):
        return False
    return True


## A path acceptor which skips parsley control stuff. It is always used.
def builtinpathacceptor(p):
    bn = os.path.basename(p)
    if bn == ".parsley.control":
        return False
    return True

