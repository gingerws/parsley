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

from parsley.engine import *


## Just a helping hand for testing/debugging parsley from within the IDE, but not really needed for a release version.
def check4debugtest():
    import sys
    import os
    if len(sys.argv) > 1 and sys.argv[1] == "_debugtest":
        preplogging = Logger(loggerout=FilestreamLoggerout(), formatter=PlaintextLogformat(color=2),
                             minseverity=Severity.DEBUGVERBOSE, maxseverity=Severity.ERROR)
        if not os.path.isdir("/tmp/parsleydebugtest1"):
            os.makedirs("/tmp/parsleydebugtest1/.parsley.control")
            preplogging.log("preparation", "parsley dir /tmp/parsleydebugtest1", "created", "", Severity.IMPORTANT, "!")
        if not os.path.isdir("/tmp/parsleydebugtest2"):
            os.makedirs("/tmp/parsleydebugtest2/.parsley.control")
            preplogging.log("preparation", "parsley dir /tmp/parsleydebugtest2", "created", "", Severity.IMPORTANT, "!")
        if not os.path.isdir("/tmp/parsleydebugtest_data"):
            os.makedirs("/tmp/parsleydebugtest_data")
            preplogging.log("preparation", "datadir /tmp/parsleydebugtest_data", "created", "", Severity.IMPORTANT, "!")
        sync = InFsSync(
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)), path="/tmp/parsleydebugtest1", name="t1"),
            LocalFilesystem(TrashRemove(trashdelay=timedelta(seconds=10)), path="/tmp/parsleydebugtest2", name="t2"),
            DefaultSync(),
            Logging(logupdate=True, logcreate=True, logremove=True),
            host="localhost", name="debugtest",
            interval=timedelta(seconds=0))
        logging = Logger(loggerout=FilestreamLoggerout(), formatter=PlaintextLogformat(color=4),
                         minseverity=Severity.DEBUGVERBOSE, maxseverity=Severity.ERROR)
        Engine().execute([sync], "/tmp/parsleydebugtest_data", "localhost~debugtest", [logging], throwexceptions=True)
        sys.exit(0)

if __name__ == "__main__":
    check4debugtest()
    main()

