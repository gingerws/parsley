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
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.aspect.applypathacceptor import ApplyPathAcceptor
from parsley.sync.infs.aspect.collectinformation import CollectInformation
from parsley.sync.infs.aspect.conflicts import DetectTypeConflicts
from parsley.sync.infs.aspect.defaultiteration import DefaultIteration
from parsley.sync.infs.aspect.detectfilesystemmtimeprecision import DetectFilesystemMtimePrecision
from parsley.sync.infs.aspect.electmaster import ElectMasterFileByMtime, ElectMasterLinkByTargetHistory
from parsley.sync.infs.aspect.parsleycontroldir import CreateParsleyControlDirectory
from parsley.sync.infs.aspect.peekfilesystemalive import PeekFilesystemAlive
from parsley.sync.infs.aspect.remove import DetectRemoval, DefaultRemoveDirs
from parsley.sync.infs.aspect.update import DefaultUpdateFile, DefaultUpdateLink
from parsley.tools.pathacceptors import builtinpathacceptor
from parsley.sync.infs.syncmachine import SyncHooks


## Basic part of default behavior for a plain synchronization.
class DefaultBase(Aspect):
    def __init__(self):
        DefaultIteration.__init__(self)
        CollectInformation.__init__(self)
        ElectMasterFileByMtime.__init__(self)
        ElectMasterLinkByTargetHistory.__init__(self)
        ApplyPathAcceptor.__init__(self, builtinpathacceptor)
        DetectFilesystemMtimePrecision.__init__(self)
        CreateParsleyControlDirectory.__init__(self)
        PeekFilesystemAlive.__init__(self)

    def hook(self, machine, isglobal, fss):
        DefaultIteration.hook(self, machine, isglobal, fss)
        CollectInformation.hook(self, machine, isglobal, fss)
        ElectMasterFileByMtime.hook(self, machine, isglobal, fss)
        ElectMasterLinkByTargetHistory.hook(self, machine, isglobal, fss)
        ApplyPathAcceptor.hook(self, machine, isglobal, fss)
        DetectFilesystemMtimePrecision.hook(self, machine, isglobal, fss)
        CreateParsleyControlDirectory.hook(self, machine, isglobal, fss)
        PeekFilesystemAlive.hook(self, machine, isglobal, fss)


## Default behavior for a plain synchronization.
class DefaultSync(DefaultBase):
    def __init__(self):
        DefaultBase.__init__(self)
        DefaultUpdateFile.__init__(self)
        DefaultUpdateLink.__init__(self)
        DetectTypeConflicts.__init__(self)
        DetectRemoval.__init__(self)
        DefaultRemoveDirs.__init__(self)

    def hook(self, machine, isglobal, fss):
        DefaultBase.hook(self, machine, isglobal, fss)
        DefaultUpdateFile.hook(self, machine, isglobal, fss)
        DefaultUpdateLink.hook(self, machine, isglobal, fss)
        DetectTypeConflicts.hook(self, machine, isglobal, fss)
        DetectRemoval.hook(self, machine, isglobal, fss)
        DefaultRemoveDirs.hook(self, machine, isglobal, fss)


## Default behavior for a source filesystem in a pull-and-purge configuration.
class PullAndPurgeSyncSource(Aspect):
    def __init__(self):
        DefaultIteration.__init__(self)
        CollectInformation.__init__(self)
        ElectMasterFileByMtime.__init__(self)
        ElectMasterLinkByTargetHistory.__init__(self)
        DetectFilesystemMtimePrecision.__init__(self)
        CreateParsleyControlDirectory.__init__(self)
        PeekFilesystemAlive.__init__(self)
        ApplyPathAcceptor.__init__(self, builtinpathacceptor, _dontthrowexceptiononnonglobalusage=True)

    def hook(self, machine, isglobal, fss):
        DefaultIteration.hook(self, machine, isglobal, fss)
        CollectInformation.hook(self, machine, isglobal, fss)
        ElectMasterFileByMtime.hook(self, machine, isglobal, fss)
        ElectMasterLinkByTargetHistory.hook(self, machine, isglobal, fss)
        DetectFilesystemMtimePrecision.hook(self, machine, isglobal, fss)
        CreateParsleyControlDirectory.hook(self, machine, isglobal, fss)
        PeekFilesystemAlive.hook(self, machine, isglobal, fss)
        ApplyPathAcceptor.hook(self, machine, isglobal, fss)


## Default behavior for a sink filesystem in a pull-and-purge configuration.
class PullAndPurgeSyncSink(Aspect):
    def __init__(self):
        DefaultUpdateFile.__init__(self)

    ## Renames an existing existing entry to some new name.
    @staticmethod
    def _rename_existing_to_new_name(fs):
        def _x(srcfs, path, runtime):
            _p = path
            i = 1
            _pd = os.path.dirname(path)
            _pb = os.path.basename(path)
            _pi = _pb.rfind(".")
            rename = False
            while fs.exists(_p):
                rename = True
                if _pi > 0:  # sic!
                    _p = "{pd}/{pb1}.{i}.{pb2}".format(pd=_pd, pb1=_pb[:_pi], i=i, pb2=_pb[_pi + 1:])
                else:
                    _p = path + "." + str(i)
                i += 1
            if rename:
                fs.move(path, _p)
                runtime.changed_flag = True
        return _x

    ## Removes the file in the source filesystem.
    @staticmethod
    def _remove_from_source_filesystem():
        def _x(srcfs, path, runtime):
            srcfs.removefile(path)
        return _x

    def hook(self, machine, isglobal, fss):
        DefaultUpdateFile.hook(self, machine, isglobal, fss)
        for fs in fss:
            machine.addhook(fs, SyncHooks.onupdatefile, 10000, PullAndPurgeSyncSink._rename_existing_to_new_name(fs))
            machine.addhook(fs, SyncHooks.onupdatefile, 80000, PullAndPurgeSyncSink._remove_from_source_filesystem())
