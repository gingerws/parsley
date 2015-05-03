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

##@package parsley.runtime.commonimports
## Imports everything which is typically used by the end user in a parsley config file.

from datetime import timedelta
from parsley.tools.pathacceptors import defaultpathacceptor
from parsley.sync.infs import InFsSync
from parsley.sync.infs.filesystem.local import LocalFilesystem
from parsley.sync.infs.filesystem.sshfs import SshfsFilesystem
from parsley.preparations.mountpreparation import MountPreparation
from parsley.preparations.sshfsmountpreparation import SshfsMountPreparation
from parsley.logger.logger import Logger
from parsley.logger.loggerout.externalprogramloggerout import ExternalProgramLoggerout
from parsley.logger.loggerout.filestreamloggerout import FilestreamLoggerout
from parsley.logger.formatter.plaintextlogformat import PlaintextLogformat
from parsley.logger.formatter.htmllogformat import HtmlLogformat
from parsley.sync.infs.aspect.remove import TrashRemove, DefaultRemove
from parsley.sync.infs.aspect.logging import Logging
from parsley.sync.infs.aspect.defaults import DefaultSync, PullAndPurgeSyncSink, PullAndPurgeSyncSource
from parsley.sync.infs.aspect.revisiontracking import RevisionTracking
from parsley.sync.infs.aspect.applypathacceptor import ApplyPathAcceptor

try:
    import stat
    from parsley.sync.infs.aspect.permissions import ApplyPermissions
except Exception:
    pass

try:
    from parsley.sync.infs.aspect.metadata import MetadataSynchronization, MetadataSynchronizationWithShadow
except Exception:
    pass
