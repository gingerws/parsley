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
import xml.etree.cElementTree as xml
from parsley.logger.severity import Severity
from parsley.sync.infs import Filesystem
from parsley.sync.infs.aspect import Aspect
from parsley.sync.infs.syncmachine import SyncHooks

class _Metadata:

    def __str__(self):
        return "[v:{v} data:{d}]".format(v=self.version, d=str(self._data))

    def __init__(self, version=0):
        self.version = version
        self._data = {}

    def putdata(self, k, v):
        self._data[k] = v

    def getdata(self, k, d=None):
        return self._data.get(k, d)

    def getkeys(self):
        return list(self._data.keys())

    @staticmethod
    def get_metadata_from_file(fs, path, ignore_removed=False):
        if fs.exists(path):
            xakeys = fs.listxattrkeys(path)
            version = -1
            if "user.parsley__version" in xakeys:
                version = int(fs.getxattrvalue(path, "user.parsley__version"))
            result = _Metadata(version)
            for xakey in xakeys:
                if xakey.startswith("user.parsley_"):
                    key = xakey[13:]
                    if key != "_version":
                        value = fs.getxattrvalue(path, xakey)
                        result.putdata(key, value)
        else:
            if ignore_removed:
                result = _Metadata(-1)
            else:
                raise Exception("file {path} does not exist on {fs}".format(path=path, fs=fs.name))
        return result

    @staticmethod
    def set_metadata_to_file(fs, path, md, ignore_removed=False):
        if fs.exists(path):
            xakeys = fs.listxattrkeys(path)
            for key in md._data.keys():
                xakey = "user.parsley_"+key
                fs.setxattrvalue(path, xakey, md._data[key])
                if xakey in xakeys:
                    xakeys.remove(xakey)
            for xakey in xakeys:
                if xakey.startswith("user.parsley_") and xakey != "user.parsley__version":
                    fs.unsetxattrvalue(path, xakey)
            _Metadata.set_metadataversion_to_file(fs, path, md, ignore_removed)
        else:
            if not ignore_removed:
                raise Exception("file {path} does not exist on {fs}".format(path=path, fs=fs.name))

    @staticmethod
    def set_metadataversion_to_file(fs, path, md, ignore_removed=False):
        if fs.exists(path):
            fs.setxattrvalue(path, "user.parsley__version", str(md.version))
        else:
            if not ignore_removed:
                raise Exception("file {path} does not exist on {fs}".format(path=path, fs=fs.name))

    @staticmethod
    def get_metadata_from_shadow(fs, path):
        isdir = fs.getftype(path) == Filesystem.Directory
        xmlpath = "/.parsley.control/content_metadata/" + path \
                  + ("/##parsley.directory.metadata##" if isdir else "")
        if fs.getftype(xmlpath) == Filesystem.File:
            root = xml.parse(fs.getfulllocalpath(xmlpath)).getroot()
            res = _Metadata(version=int(root.attrib["version"]))
            for xmlchild in root:
                res.putdata(xmlchild.attrib["key"], xmlchild.attrib["value"])
        else:
            res = _Metadata(version=-1)
        return res

    @staticmethod
    def set_metadata_to_shadow(fs, path, md):
        isdir = fs.getftype(path) == Filesystem.Directory
        root = xml.Element("parsley_metadata")
        root.set("version", str(md.version))
        for kkey in md.getkeys():
            ent = xml.SubElement(root, "item")
            ent.set("key", kkey)
            ent.set("value", md.getdata(kkey, ""))
        tree = xml.ElementTree(root)
        destfile = os.path.abspath("/.parsley.control/content_metadata/" + path
                                   + ("/##parsley.directory.metadata##" if isdir else ""))
        destdir = os.path.dirname(destfile)
        fs.createdirs(destdir)
        tree.write(fs.getfulllocalpath(destfile), encoding="utf-8")

    @staticmethod
    def remove_shadow(fs, path, isdir):
        destfile = os.path.abspath("/.parsley.control/content_metadata/" + path
                                   + ("/##parsley.directory.metadata##" if isdir else ""))
        if isdir:
            destdir = os.path.dirname(destfile)
            if fs.exists(destdir):
                fs.removedir(destdir, recursive=True)
        else:
            if fs.exists(destfile):
                fs.removefile(destfile)

    @staticmethod
    def metadata_differs(md1, md2):
        return md1.version != md2.version or md1._data != md2._data


class _MyTaskData:
    def __init__(self):
        self.latestmd = None
        self.latestmd_origversion = -1
        self.aborted = False
        self.forpath = None


## Synchronizes metadata without a shadow storage (typical for the workstations)
class MetadataSynchronization(Aspect):
    def __init__(self):
        Aspect.__init__(self)

    def _taskdatakey(self, runtime):
        return str(id(runtime.currentsync)) + "/MetadataSynchronization"

    @staticmethod
    def _checkupdatesagainstshadow_helper(_fs, path, machine, runtime, taskdatakey):
        if not taskdatakey(runtime) in runtime.taskdata:
            raise Exception("At least one metadata synchronization with shadow must exist.")
        td = runtime.taskdata[taskdatakey(runtime)]
        if td.aborted:
            return
        minemd = _Metadata.get_metadata_from_file(_fs, path, ignore_removed=True)
        if minemd.version >= td.latestmd.version:
            if _Metadata.metadata_differs(minemd, td.latestmd):
                if minemd.version == td.latestmd.version or td.latestmd_origversion == -1:
                    if minemd.version == td.latestmd_origversion:
                        minemd.version += 1
                        td.latestmd = minemd
                    elif td.latestmd_origversion == -1:
                        td.latestmd = minemd
                        td.latestmd_origversion = minemd.version
                    else:
                        td.aborted = True
                        machine.logproblem(_fs, path, runtime, verb="has metadata conflict.")

    @staticmethod
    def _propagatetofile_helper(_fs, path, machine, runtime, taskdatakey):
        td = runtime.taskdata[taskdatakey(runtime)]
        if td.aborted or td.latestmd.version < 0:
            return
        if _Metadata.metadata_differs(td.latestmd, _Metadata.get_metadata_from_file(_fs, path, ignore_removed=True)):
            if _fs.exists(path):
                _Metadata.set_metadata_to_file(_fs, path, td.latestmd)
                machine.logupdate(_fs, "metadata of " + path, runtime, comment="on "+_fs.name)
            else:
                machine.logproblem(_fs, path, runtime, verb="gone during metadata update", severity=Severity.DEBUG)
            runtime.changed_flag = True

    ## Checks if this entry has a metadata update against the shadow storage. If so, it updates the version numbers
    ## (in the in-memory data structure).
    @staticmethod
    def _checkupdatesagainstshadow_dir(fs, machine, taskdatakey):
        def _x(path, runtime):
            return MetadataSynchronization._checkupdatesagainstshadow_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Checks if metadata of the entry differ from the shadow storage information and, if so, updates the
    ## entry metadata in the filesystem (with exactly what it is now stored in-memory).
    @staticmethod
    def _propagatetofilesystem_dir(fs, machine, taskdatakey):
        def _x(path, runtime):
            return MetadataSynchronization._propagatetofile_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Checks if this entry has a metadata update against the shadow storage. If so, it updates the version numbers
    ## (in the in-memory data structure).
    @staticmethod
    def _checkupdatesagainstshadow_file(fs, machine, taskdatakey):
        def _x(srcfs, path, wasremoved, runtime):
            return MetadataSynchronization._checkupdatesagainstshadow_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Checks if metadata of the entry differ from the shadow storage information and, if so, updates the
    ## entry metadata in the filesystem (with exactly what it is now stored in-memory).
    @staticmethod
    def _propagatetofilesystem_file(fs, machine, taskdatakey):
        def _x(srcfs, path, wasremoved, runtime):
            return MetadataSynchronization._propagatetofile_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    def hook(self, machine, isglobal, fss):
        for fs in fss:
            machine.addhook(fs, SyncHooks.onendupdatedir, 60001, MetadataSynchronization._checkupdatesagainstshadow_dir(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendupdatedir, 60002, MetadataSynchronization._propagatetofilesystem_dir(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendprocessfile, 60001, MetadataSynchronization._checkupdatesagainstshadow_file(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendprocessfile, 60002, MetadataSynchronization._propagatetofilesystem_file(fs, machine, self._taskdatakey))


## Synchronizes metadata with a shadow storage (typical for the file server)
class MetadataSynchronizationWithShadow(MetadataSynchronization):

    def __init__(self):
        MetadataSynchronization.__init__(self)

    @staticmethod
    def _findhighestshadow_helper(_fs, path, machine, runtime, taskdatakey):
        if not taskdatakey(runtime) in runtime.taskdata \
                or runtime.taskdata[taskdatakey(runtime)].forpath != path:
            md = _Metadata(-1)
            td = _MyTaskData()
            td.latestmd = md
            runtime.taskdata[taskdatakey(runtime)] = td
        else:
            td = runtime.taskdata[taskdatakey(runtime)]
        minemd = _Metadata.get_metadata_from_shadow(_fs, path)
        if minemd.version > td.latestmd.version:
            td.latestmd = minemd
            td.latestmd_origversion = minemd.version
        elif minemd.version == td.latestmd.version and \
                _Metadata.metadata_differs(minemd, td.latestmd):
            machine.logproblem(_fs, path, runtime, verb="has metadata conflict with shadow")
            td.aborted = True

    @staticmethod
    def _propagatetoshadow_helper(_fs, path, machine, runtime, taskdatakey):
        td = runtime.taskdata[taskdatakey(runtime)]
        if td.aborted or td.latestmd.version < 0:
            return
        if _Metadata.metadata_differs(td.latestmd, _Metadata.get_metadata_from_shadow(_fs, path)):
            _Metadata.set_metadata_to_shadow(_fs, path, td.latestmd)
            runtime.changed_flag = True

    ## Updates `latestmd` as stored in taskdata if this filesystem has a higher version in shadow.
    @staticmethod
    def _findhighestshadow_dir(fs, machine, taskdatakey):
        def _x(path, runtime):
            return MetadataSynchronizationWithShadow._findhighestshadow_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Checks if metadata of the entry differ from the shadow storage information and, if so, updates the
    ## entry metadata in the shadow storage (with exactly what it is now stored in-memory).
    @staticmethod
    def _propagatetoshadow_dir(fs, machine, taskdatakey):
        def _x(path, runtime):
            return MetadataSynchronizationWithShadow._propagatetoshadow_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Updates `latestmd` as stored in taskdata if this filesystem has a higher version in shadow.
    @staticmethod
    def _findhighestshadow_file(fs, machine, taskdatakey):
        def _x(srcfs, path, wasremoved, runtime):
            return MetadataSynchronizationWithShadow._findhighestshadow_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Checks if metadata of the entry differ from the shadow storage information and, if so, updates the
    ## entry metadata in the shadow storage (with exactly what it is now stored in-memory).
    @staticmethod
    def _propagatetoshadow_file(fs, machine, taskdatakey):
        def _x(srcfs, path, wasremoved, runtime):
            return MetadataSynchronizationWithShadow._propagatetoshadow_helper(fs, path, machine, runtime, taskdatakey)
        return _x

    ## Removes the shadow storage information for this entry, if it does not even exist anymore in the filesystem.
    @staticmethod
    def _removeshadow_dir(fs):
        def _x(path, runtime):
            if not fs.exists(path):
                _Metadata.remove_shadow(fs, path, True)
        return _x

    ## Removes the shadow storage information for this entry, if it does not even exist anymore in the filesystem.
    @staticmethod
    def _removeshadow_file(fs):
        def _x(srcfs, path, runtime):
            _Metadata.remove_shadow(fs, path, False)
        return _x

    def hook(self, machine, isglobal, fss):
        MetadataSynchronization.hook(self, machine, isglobal, fss)
        for fs in fss:
            machine.addhook(fs, SyncHooks.onendupdatedir, 60000, MetadataSynchronizationWithShadow._findhighestshadow_dir(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendupdatedir, 60002, MetadataSynchronizationWithShadow._propagatetoshadow_dir(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendprocessfile, 60000, MetadataSynchronizationWithShadow._findhighestshadow_file(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendprocessfile, 60002, MetadataSynchronizationWithShadow._propagatetoshadow_file(fs, machine, self._taskdatakey))
            machine.addhook(fs, SyncHooks.onendupdatedir, 60000, MetadataSynchronizationWithShadow._removeshadow_dir(fs))
            machine.addhook(fs, SyncHooks.onremovefile, 60000, MetadataSynchronizationWithShadow._removeshadow_file(fs))
