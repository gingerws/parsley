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

from parsley.logger.formatter import Logformat
from parsley.logger.severity import Severity


class HtmlLogformat(Logformat):

    def __init__(self):
        Logformat.__init__(self)
        self.bgtoggle = True
        self.lastsync = object()

    def header(self):
        return """
        <html><head>
        <style>
            td { padding: 2pt;}
            th { padding: 3pt; margin:0 3pt 0 0; font-size:1.2em; text-align:left; }
        </style>
        </head><body>
        <table style='border-collapse:collapse;border-width:0px;width:100%;'>
        """

    def log(self, sync, subject, verb, comment, severity, symbol):
        color = "#adcbc9"
        if severity == Severity.INFO:
            color = "#222222"
        elif severity == Severity.IMPORTANT:
            color = "#80651b"
        elif severity == Severity.MOREIMPORTANT:
            color = "#9d1e1e"
        elif severity >= Severity.ERROR:
            color = "#ff0000"
        self.bgtoggle = not self.bgtoggle
        backgroundcolor = "#EEEEEE" if self.bgtoggle else "#DDDDDD"
        if sync != self.lastsync:
            header = "<th colspan='4'>{sync}</th>".format(**locals())
            self.lastsync = sync
        else:
            header = ""
        return ("""
{header}
<tr style='color:{color};background-color:{backgroundcolor};'>
    <td>{symbol}</td>
    <td>{subject}</td>
    <td style='font-weight:bold;'>{verb}</td>
    <td>{comment}</td>
</tr>
        """).format(**locals())

    def footer(self):
        return "</table></body></html>\n"


