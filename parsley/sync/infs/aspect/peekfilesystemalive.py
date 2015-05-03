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

from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks


# Observe if the filesystems remain connected and abort otherwise.
class PeekFilesystemAlive(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    @staticmethod
    def _check(ffs):
        if len(ffs.listdir("/")) == 0:
            raise Exception("filesystem {fs} disconnected".format(fs=ffs.name))

    ## Checks if the underlying filesystem is still connected and aborts the process otherwise.
    @staticmethod
    def _crash_if_disconnected1(fs):
        def _x(path, runtime):
            PeekFilesystemAlive._check(fs)
        return _x

    ## Checks if the underlying filesystem is still connected and aborts the process otherwise.
    @staticmethod
    def _crash_if_disconnected2(fs):
        def _x(srcfs, path, runtime, recursive=None):
            PeekFilesystemAlive._check(srcfs)
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onbeginupdatedir, 20000, PeekFilesystemAlive._crash_if_disconnected1(fs))
            machine.addhook(fs, SyncHooks.onupdatefile, 50000, PeekFilesystemAlive._crash_if_disconnected2(fs))
            machine.addhook(fs, SyncHooks.onupdatelink, 50000, PeekFilesystemAlive._crash_if_disconnected2(fs))
            machine.addhook(fs, SyncHooks.onremovefile, 20000, PeekFilesystemAlive._crash_if_disconnected2(fs))
            machine.addhook(fs, SyncHooks.onremovelink, 20000, PeekFilesystemAlive._crash_if_disconnected2(fs))
            machine.addhook(fs, SyncHooks.onremovedir, 20000, PeekFilesystemAlive._crash_if_disconnected2(fs))
