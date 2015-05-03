#!/usr/bin/python3
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

##@package parsley.test.test13
## Test: metadata simple

if "syncs" in globals():

    # noinspection PyUnresolvedReferences
    syncs.append(
        InFsSync(
            LocalFilesystem(
                TrashRemove(),
                MetadataSynchronizationWithShadow(),
                path="m", name="master"),
            LocalFilesystem(
                TrashRemove(),
                MetadataSynchronization(),
                path="s", name="slave"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="test",
            interval=timedelta(seconds=0)
        ))

else:
    import sys
    sys.path.append("../..")
    from parsley.test.test import *

    write2file("m/d/dummy", "dummy")
    write2file("m/d2/dummy", "dummy")
    write2file("m/f1", "f1")
    write2file("m/f2", "f2")
    write2file("s/f3", "f3")
    write2file("s/f4", "f4")
    metadata.setfilemetadata("m/f1", "foo", "1")
    metadata.setfilemetadata("m/f2", "foo", "2")
    metadata.setfilemetadata("s/f3", "foo", "3")
    metadata.setfilemetadata("s/f4", "foo", "4")
    metadata.setfilemetadata("m/d", "foo", "d")
    metadata.setfilemetadata("m/d/dummy", "foo", "dummy")

    SYNC()

    verify(metadata.getfilemetadata("m/f1", "foo") == "1", "m f1 metadata 1")
    verify(metadata.getfilemetadata("s/f1", "foo") == "1", "s f1 metadata 1")
    verify(metadata.getfilemetadata("m/f2", "foo") == "2", "m f2 metadata 2")
    verify(metadata.getfilemetadata("s/f2", "foo") == "2", "s f2 metadata 2")
    verify(metadata.getfilemetadata("m/f3", "foo") == "3", "m f3 metadata 3")
    verify(metadata.getfilemetadata("s/f3", "foo") == "3", "s f3 metadata 3")
    verify(metadata.getfilemetadata("m/f4", "foo") == "4", "m f4 metadata 4")
    verify(metadata.getfilemetadata("s/f4", "foo") == "4", "s f4 metadata 4")
    verify(metadata.getfilemetadata("m/d", "foo") == "d", "m d metadata d")
    verify(metadata.getfilemetadata("s/d", "foo") == "d", "s d metadata d")
    verify(metadata.getshadowmetadata("m/f1", "foo") == "1", "m f1 shadowmetadata 1")
    verify(metadata.getshadowmetadata("m/f2", "foo") == "2", "m f2 shadowmetadata 2")
    verify(metadata.getshadowmetadata("m/f3", "foo") == "3", "m f3 shadowmetadata 3")
    verify(metadata.getshadowmetadata("m/f4", "foo") == "4", "m f4 shadowmetadata 4")
    verify(metadata.getshadowmetadata("m/d", "foo") == "d", "m d shadowmetadata d")
    verify(metadata.getfilemetadata("m/f1", "_version") == "0", "m f1 metadataversion")
    verify(metadata.getfilemetadata("s/f1", "_version") == "0", "s f1 metadataversion")
    verify(metadata.getfilemetadata("m/f2", "_version") == "0", "m f2 metadataversion")
    verify(metadata.getfilemetadata("s/f2", "_version") == "0", "s f2 metadataversion")
    verify(metadata.getfilemetadata("m/f3", "_version") == "0", "m f3 metadataversion")
    verify(metadata.getfilemetadata("s/f3", "_version") == "0", "s f3 metadataversion")
    verify(metadata.getfilemetadata("m/f4", "_version") == "0", "m f4 metadataversion")
    verify(metadata.getfilemetadata("s/f4", "_version") == "0", "s f4 metadataversion")
    verify(metadata.getfilemetadata("m/d", "_version") == "0", "m d metadataversion")
    verify(metadata.getfilemetadata("s/d", "_version") == "0", "s d metadataversion")
    verify(metadata.getshadowmetadata("m/f1", "_version") == "0", "m f1 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/f2", "_version") == "0", "m f2 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/f3", "_version") == "0", "m f3 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/f4", "_version") == "0", "m f4 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/d", "_version") == "0", "m d shadowmetadataversion")
    verify(metadata.getfilemetadata("m/d2", "_version") == None, "m d2 no metadata")
    verify(metadata.getfilemetadata("s/d2", "_version") == None, "s d2 no metadata")
    verify(metadata.getfilemetadata("m/d2/dummy", "_version") == None, "m dummy no metadata")
    verify(metadata.getfilemetadata("s/d2/dummy", "_version") == None, "s dummy no metadata")
    verify(metadata.getshadowmetadata("m/d2", "_version") == None, "m d2 no shadowmetadata")
    verify(metadata.getshadowmetadata("m/d2/dummy", "_version") == None, "m dummy no shadowmetadata")

    SYNC()

    verify(metadata.getfilemetadata("m/d", "_version") == "0", "m d metadataversion")
    verify(metadata.getfilemetadata("s/d", "_version") == "0", "s d metadataversion")
    verify(metadata.getfilemetadata("m/d", "foo") == "d", "m d metadata d")
    verify(metadata.getfilemetadata("s/d", "foo") == "d", "s d metadata d")
    verify(metadata.getshadowmetadata("m/d", "foo") == "d", "m d shadowmetadata d")

    metadata.setfilemetadata("s/f1", "foo", "1A")
    metadata.setfilemetadata("s/f3", "foo", "3A")
    metadata.setfilemetadata("s/d", "foo", "dA")
    metadata.setshadowmetadata("m/f2", "foo", "2A")
    metadata.killshadowmetadata("m/f4")

    SYNC()

    verify(metadata.getfilemetadata("m/f1", "foo") == "1A", "m f1 metadata 1A")
    verify(metadata.getfilemetadata("s/f1", "foo") == "1A", "s f1 metadata 1A")
    verify(metadata.getfilemetadata("m/f2", "foo") == "2A", "m f2 metadata 2A")
    verify(metadata.getfilemetadata("s/f2", "foo") == "2A", "s f2 metadata 2A")
    verify(metadata.getfilemetadata("m/f3", "foo") == "3A", "m f3 metadata 3A")
    verify(metadata.getfilemetadata("s/f3", "foo") == "3A", "s f3 metadata 3A")
    verify(metadata.getfilemetadata("m/f4", "foo") == "4", "m f4 metadata 4")
    verify(metadata.getfilemetadata("s/f4", "foo") == "4", "s f4 metadata 4")
    verify(metadata.getfilemetadata("m/d", "foo") == "dA", "m d metadata dA")
    verify(metadata.getfilemetadata("s/d", "foo") == "dA", "s d metadata dA")
    verify(metadata.getshadowmetadata("m/f1", "foo") == "1A", "m f1 shadowmetadata 1A")
    verify(metadata.getshadowmetadata("m/f2", "foo") == "2A", "m f2 shadowmetadata 2A")
    verify(metadata.getshadowmetadata("m/f3", "foo") == "3A", "m f3 shadowmetadata 3A")
    verify(metadata.getshadowmetadata("m/f4", "foo") == "4", "m f4 shadowmetadata 4")
    verify(metadata.getshadowmetadata("m/d", "foo") == "dA", "m d shadowmetadata dA")
    verify(metadata.getfilemetadata("m/f1", "_version") == "1", "m f1 metadataversion")
    verify(metadata.getfilemetadata("s/f1", "_version") == "1", "s f1 metadataversion")
    verify(metadata.getfilemetadata("m/f2", "_version") == "1", "m f2 metadataversion")
    verify(metadata.getfilemetadata("s/f2", "_version") == "1", "s f2 metadataversion")
    verify(metadata.getfilemetadata("m/f3", "_version") == "1", "m f3 metadataversion")
    verify(metadata.getfilemetadata("s/f3", "_version") == "1", "s f3 metadataversion")
    verify(metadata.getfilemetadata("m/f4", "_version") == "0", "m f4 metadataversion")
    verify(metadata.getfilemetadata("s/f4", "_version") == "0", "s f4 metadataversion")
    verify(metadata.getfilemetadata("m/d", "_version") == "1", "m d metadataversion")
    verify(metadata.getfilemetadata("s/d", "_version") == "1", "s d metadataversion")
    verify(metadata.getshadowmetadata("m/f1", "_version") == "1", "m f1 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/f2", "_version") == "1", "m f2 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/f3", "_version") == "1", "m f3 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/f4", "_version") == "0", "m f4 shadowmetadataversion")
    verify(metadata.getshadowmetadata("m/d", "_version") == "1", "m d shadowmetadataversion")
    verify(metadata.getfilemetadata("m/d2", "_version") == None, "m d2 no metadata")
    verify(metadata.getfilemetadata("s/d2", "_version") == None, "s d2 no metadata")
    verify(metadata.getfilemetadata("m/d2/dummy", "_version") == None, "m dummy no metadata")
    verify(metadata.getfilemetadata("s/d2/dummy", "_version") == None, "s dummy no metadata")
    verify(metadata.getshadowmetadata("m/d2", "_version") == None, "m d2 no shadowmetadata")
    verify(metadata.getshadowmetadata("m/d2/dummy", "_version") == None, "m dummy no shadowmetadata")

    deletedir("s/d")

    SYNC()

    verify(metadata.getfilemetadata("m/d/dummy", "_version") == None, "s dummy no metadata")
    verify(metadata.getfilemetadata("s/d/dummy", "_version") == None, "s dummy no metadata")
    verify(metadata.getshadowmetadata("m/d/dummy", "_version") == None, "m dummy no shadowmetadata")
    verify(metadata.getfilemetadata("m/d", "_version") == None, "s d no metadata")
    verify(metadata.getfilemetadata("s/d", "_version") == None, "s d no metadata")
    verify(metadata.getshadowmetadata("m/d", "_version", hint_isdir=True) == None, "m d no shadowmetadata")

