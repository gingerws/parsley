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

##@package parsley.sync.infs
## The included powerful synchronization implementation.

from parsley.sync.abstract.sync import Sync
from .filesystem import Filesystem
from .aspect import Aspect
from .syncmachine import SyncMachine
from .common import *

## The included powerful synchronization implementation.
##
## Parsley configuration files typically create some instances of this class.
##
## It can synchronize files between some filesystems with a
## behavior defined by aspects. Put instances of parsley.sync.infs.filesystem.Filesystem and
## parsley.sync.infs.aspect.Aspect as parameters into this constructor for defining them.
##
## Aspects as well as filesystems may be custom implementations, although parsley includes many useful implementations.
##
## This synchronization task mostly is a workflow around event handlers which come from the aspects. They will be
## executed when a certain state in the workflow is reached. The following workflow description
## explains informally how the workflow is defined. The authoritative definition of course is the source code :-P
##
## Be aware of some things:
## - Whenever an event occurs, this description lists all the event handlers from all the aspects which are
##   included in parsley. Other aspects which could come from outside are obviously not mentioned.
## - Sometimes the aspects which own this event handlers are very common ones, and sometimes they are rather
##   exotic. Please check which aspects are really included in your actual configuration.
## - Aspects often inherit the behaviour of other ones. This is sometimes not even visible due to the class
##   hierarchy; for technical reasons of course, not because i'm lazy ;) You can only find that out in the
##   documentation (hint: from the 'subclasses' upwards) !
## - Similar things are true for filesystem: They can also implicitely put new aspects into the configuration.
## - The event handlers always get called in the defined order. This has a dramatic
##   influence, since they often, for instance, can skip the following handlers.
## - Sometimes the list simply mentions 'none', which then means just that :)
## - Each event handler is (potentially, of course) called for each of the defined filesystems. This can also depend
##   on the situation (the following text will mention that). However, every time an event handler eventually get
##   executed, this happens upon one filesystem and for one entry specified by a relative path. Other parameters may
##   exist as well (see the (linked) `SyncHooks` documentations).
## - When an event occurs on more than one filesystem, the execution order can be grouped by filesystem first or by
##   event handler first. The former means, at first all the handlers for filesystem 1 are executed, then all the
##   handlers for filesystem 2, and so on. The latter one means, at first the first handler is executed for all
##   filesystems, then the second handler is executed for all filesystems, and so on. You find this information
##   in the `SyncHooks` documentations.
##
## Before the base process begins, the `parsley.sync.infs.syncmachine.SyncHooks.onbeginsync` event occurs
## (note: this is an exceptional case of a event which is *not* called for a certain path!), which
## has the following handlers:
## \copydoc HOOK1_ONBEGINSYNC
##
## The base process itself works recursively. It is called once at the beginning with a start parameter and from
## time to time calls itself (with a different parameter).
##
## This parameter specifies the current directory, i.e. what the process should process in that run. This is relative
## to the root paths of the affected filesystems. Those paths aren't bound to a certain filesystem but should be seen
## as common locations (like `pics/a.jpg`). However, it may of course happen that a certain path does not exist on all
## involved filesystems.
##
## When the recursive base process starts (as it is initially started on directory `/`), it calls
## `parsley.sync.infs.syncmachine.SyncHooks.onbeginupdatedir` which has this handlers:
## \copydoc HOOK1_ONBEGINUPDATEDIR
##
## It then collects a list of all entries which live somewhere in the specified directory. By prepending the
## path of the current directory, we get the child path. It gets the list by calling
## `parsley.sync.infs.syncmachine.SyncHooks.onlistdir` on each filesystem, which can mean this handlers:
## \copydoc HOOK1_ONLISTDIR
##
## For each entry from that iteration, it does the following:
##
## - It elects a master filesystem (the one which is considered as up-to-date). This will be used later as the
##   source for update operations. It does so by calling `parsley.sync.infs.syncmachine.SyncHooks.onelectmaster` with
## this handlers:
## \copydoc HOOK2_ONELECTMASTER
##
## - After the master filesystem is elected, the `parsley.sync.infs.syncmachine.SyncHooks.onmasterelected` event with
## this handlers occur:
## \copydoc HOOK2_ONMASTERELECTED
##
## - If there is an existing entry with that child path on the master filesystem, do the following:
##
##  - At first, check if the entry exists in all filesystems and has the same type in each (file, dir, link).
##    If not, some events occur:
##
##   - On the master filesystem, `parsley.sync.infs.syncmachine.SyncHooks.ontypeconflictmaster` with this handlers:
## \copydoc HOOK4_ONTYPECONFLICTMASTER
##
##   - On the slave filesystem, `parsley.sync.infs.syncmachine.SyncHooks.ontypeconflictslave` with this handlers:
## \copydoc HOOK4_ONTYPECONFLICTSLAVE
##
##  - Afterwards,  depending on the entry type (on the master), either
## `parsley.sync.infs.syncmachine.SyncHooks.onupdatefile` is called wih this handlers:
## \copydoc HOOK3_ONUPDATEFILE
##
##  - or `parsley.sync.infs.syncmachine.SyncHooks.onupdatelink` with handlers:
## \copydoc HOOK3_ONUPDATELINK
##
##  - or (for directories) the base process is now recursively called for that child directory.
##
##  - Afterwards, depending on the entry type it calls `parsley.sync.infs.syncmachine.SyncHooks.onendprocessfile` with:
## \copydoc HOOK3_ONENDPROCESSFILE
##
##  - or `parsley.sync.infs.syncmachine.SyncHooks.onendprocesslink` with handlers:
## \copydoc HOOK3_ONENDPROCESSLINK
##
## - otherwise, do the following:
##
##  - depending on the entry type (on the master), either `parsley.sync.infs.syncmachine.SyncHooks.onremovefile` is
## called with:
## \copydoc HOOK3_ONREMOVEFILE
##
##  - or `parsley.sync.infs.syncmachine.SyncHooks.onremovedir` (*with recursive flag*) with handlers:
## \copydoc HOOK3_ONREMOVEDIR
##
##  - or `parsley.sync.infs.syncmachine.SyncHooks.onremovelink` with handlers:
## \copydoc HOOK3_ONREMOVELINK
##
##  - Afterwards, depending on the entry type it calls `parsley.sync.infs.syncmachine.SyncHooks.onendprocessfile` with:
## \copydoc HOOK3_ONENDPROCESSFILE
##
##  - or `parsley.sync.infs.syncmachine.SyncHooks.onendprocesslink` with handlers:
## \copydoc HOOK3_ONENDPROCESSLINK
##
## At the end of the base process for that directory, it calls `parsley.sync.infs.syncmachine.SyncHooks.onendupdatedir`
## on it, with this handlers:
## \copydoc HOOK1_ONENDUPDATEDIR
##
## When the base process is completely finished for the root directory (and thereby for *all* directories)
## it calls `parsley.sync.infs.syncmachine.SyncHooks.onendsync` with this handlers:
## \copydoc HOOK1_ONENDSYNC
##
## There are also some technical events which occur not really for workflow reasons. Those are
## `parsley.sync.infs.syncmachine.SyncHooks.onlogcreate` with:
## \copydoc HOOK1_ONLOGCREATE
##
## and `parsley.sync.infs.syncmachine.SyncHooks.onlogremove` with:
## \copydoc HOOK1_ONLOGREMOVE
##
## and `parsley.sync.infs.syncmachine.SyncHooks.onlogupdate` with:
## \copydoc HOOK1_ONLOGUPDATE
##
## and `parsley.sync.infs.syncmachine.SyncHooks.onlogproblem` with:
## \copydoc HOOK1_ONLOGPROBLEM
class InFsSync(Sync):
    def __init__(self, *a, filenameacceptor=None, **b):
        Sync.__init__(self, *a, **b)
        self.filenameacceptor = filenameacceptor
        self.filesystems = []
        self.aspects = []
        self.api = None
        for x in self.cfgs:
            if isinstance(x, Filesystem):
                if x.name == "":
                    raise Exception("name must not be empty")
                if len([y for y in self.filesystems if y.name == x.name]) > 0:
                    raise Exception("names must be unique")
                self.filesystems.append(x)
            elif isinstance(x, Aspect):
                self.aspects.append(x)
            else:
                raise Exception("forbidden parameter: "+str(x))

    def execute(self, runtime):
        self.api = SyncMachine(self.filesystems, self, runtime)
        self.api.hookglobalaspects(self.aspects)
        for fs in self.filesystems:
            self.api.hookfsaspects(fs, fs.aspects)
        self.api.beginsync(runtime)
        self._syncdirs("", runtime)
        self.api.endsync(runtime)

    def initialize(self, runtime):
        for fs in self.filesystems:
            fs.initialize(self, runtime)

    def shutdown(self, runtime, crashed):
        try:
            for fs in self.filesystems:
                fs.shutdown(self, runtime)
        finally:
            self.api.shutdown(crashed)

    def _syncdirs(self, path, runtime): # do not change stuff here without changing the documentation above!!
        self.api.beginupdatedir(path, runtime)
        for f in self.api.iteratedir(path, runtime):
            fullf = path + "/" + f
            masterfs = self.api.electmaster(fullf, runtime)
            if masterfs == ElectionControl.SKIP:
                continue
            self.api.masterelected(masterfs, fullf, runtime)
            if masterfs.exists(fullf):
                ftype = masterfs.getftype(fullf)
                skip = False
                for fs in self.filesystems:
                    if fs != masterfs:
                        if fs.exists(fullf) and fs.getftype(fullf) != ftype:
                            res = self.api.resolvetypeconflict(fullf, masterfs, fs, runtime)
                            skip = res == ConflictResolution.SKIP
                            if res != ConflictResolution.NO_IDEA:
                                break
                if not skip:
                    if ftype == Filesystem.Link:
                        for fs in self.filesystems:
                            if fs != masterfs:
                                self.api.updatelink(masterfs, fullf, fs, runtime)
                    elif ftype == Filesystem.File:
                        for fs in self.filesystems:
                            if fs != masterfs:
                                self.api.updatefile(masterfs, fullf, fs, runtime)
                    elif ftype == Filesystem.Directory:
                        self._syncdirs(fullf, runtime)
                    if ftype == Filesystem.Link:
                        self.api.endprocesslink(masterfs, fullf, False, runtime)
                    elif ftype == Filesystem.File:
                        self.api.endprocessfile(masterfs, fullf, False, runtime)
            else:
                for fs in self.filesystems:
                    if fs != masterfs:
                        oftype = fs.getftype(fullf)
                        if oftype == Filesystem.File:
                            self.api.removefile(masterfs, fullf, fs, runtime)
                        elif oftype == Filesystem.Link:
                            self.api.removelink(masterfs, fullf, fs, runtime)
                        elif oftype == Filesystem.Directory:
                            self.api.removedir(masterfs, fullf, fs, runtime, recursive=True)
                if oftype == Filesystem.Link:
                    self.api.endprocesslink(masterfs, fullf, True, runtime)
                elif oftype == Filesystem.File:
                    self.api.endprocessfile(masterfs, fullf, True, runtime)
        self.api.endupdatedir(path, runtime)
