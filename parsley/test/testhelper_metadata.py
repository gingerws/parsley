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

##@package parsley.test.testhelper_metadata
## Some helper functions for implementing tests about metadata handling.

import os
import xattr
import xml.etree.cElementTree as xml


class Metadata:

    def __init__(self, mydir):
        self.mydir = mydir

    def setfilemetadata(self, p, k, v):
        _p = self.mydir + p
        xattr.set(_p, "user.parsley_"+k, v)

    def getfilemetadata(self, p, k):
        _p = self.mydir + p
        try:
            return xattr.get(_p, "user.parsley_"+k).decode("utf-8")
        except Exception:
            return None

    def getshadowmetadata(self, p, k, hint_isdir=None):
        isdir = os.path.isdir(self.mydir + p) or hint_isdir
        shadowfullpath = os.path.abspath(self.mydir + p[0:p.find("/")] + "/.parsley.control/content_metadata")
        xmlpath = shadowfullpath + "/" + p[p.find("/")+1:] + ("/##parsley.directory.metadata##" if isdir else "")
        if os.path.isfile(xmlpath):
            root = xml.parse(xmlpath).getroot()
            if k == "_version":
                return root.attrib["version"]
            for xmlchild in root:
                if xmlchild.attrib["key"] == k:
                    return xmlchild.attrib["value"]
        else:
            return None

    def setshadowmetadata(self, p, k, v):
        isdir = os.path.isdir(self.mydir + p)
        shadowfullpath = os.path.abspath(self.mydir + p[0:p.find("/")] + "/.parsley.control/content_metadata")
        xmlpath = shadowfullpath + "/" + p[p.find("/")+1:] + ("/##parsley.directory.metadata##" if isdir else "")
        root = xml.parse(xmlpath).getroot()
        root.attrib["version"] = str(int(root.attrib["version"])+1)
        for xmlchild in root:
            if xmlchild.attrib["key"] == k:
                xmlchild.attrib["value"] = v
        with open(xmlpath, "w") as f:
            f.write(xml.tostring(root).decode())

    def killshadowmetadata(self, p):
        isdir = os.path.isdir(self.mydir + p)
        shadowfullpath = os.path.abspath(self.mydir + p[0:p.find("/")] + "/.parsley.control/content_metadata")
        xmlpath = shadowfullpath + "/" + p[p.find("/")+1:] + ("/##parsley.directory.metadata##" if isdir else "")
        os.unlink(xmlpath)