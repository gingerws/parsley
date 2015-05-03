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

##@package parsley.gui.main
## The main gui for parsley (provides just common stuff for the beginning).

import os
import shutil
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import _thread
import subprocess
import parsley.tools.common
import parsley.runtime.projectinformations

home = os.path.expanduser("~").replace("\\", "/")


## A very minimalist graphical interface for creating a parsley configuration (in a very limited manner).
## Helps for the first steps with parsley, as you can directly start getting some results. Not recommended for
## everyday usage due to all its limitations.
class App(Frame):

    class FilesystemFrame(Frame):

        def __init__(self, parent, caption):
            Frame.__init__(self, parent)
            self.number = caption[0]
            self.lblFilesystem = Label(self, font=("Helvetica", 9))
            self.lblFilesystem["text"] = caption
            self.lblFilesystem.pack({"side": "top", "padx": 45, "pady": 5, "anchor": "w"})
            self.frameFilesystemRow1 = Frame(self)
            self.frameFilesystemRow1.pack({"side": "top", "fill": "x"})
            self.lblPath = Label(self.frameFilesystemRow1)
            self.lblPath["text"] = "Path:"
            self.lblPath.pack({"side": "left", "padx": 5, "pady": 5})
            self.txtPath = Entry(self.frameFilesystemRow1)
            self.txtPath.pack({"side": "left", "fill": "x", "expand": "true", "padx": 5, "pady": 5})
            self.frameFilesystemRow2 = Frame(self)
            self.frameFilesystemRow2.pack({"side": "top", "fill": "x"})
            self.varSsh = BooleanVar()
            self.chkSsh = Checkbutton(self.frameFilesystemRow2, variable=self.varSsh)
            self.chkSsh["text"] = "use SSH"
            self.chkSsh.pack({"side": "left", "padx": 5, "pady": 5})
            self.chkSsh["command"] = self._sshchanged
            self.lblPort = Label(self.frameFilesystemRow2)
            self.lblPort["text"] = "Port:"
            self.lblPort.pack({"side": "left", "padx": 5, "pady": 5})
            self.txtPort = Entry(self.frameFilesystemRow2)
            self.txtPort.pack({"side": "left", "fill": "x", "expand": "true", "padx": 5, "pady": 5})
            self.lblIdfile = Label(self.frameFilesystemRow2)
            self.lblIdfile["text"] = "Identity file:"
            self.lblIdfile.pack({"side": "left", "padx": 5, "pady": 5})
            self.txtIdfile = Entry(self.frameFilesystemRow2)
            self.txtIdfile.pack({"side": "left", "fill": "x", "expand": "true", "padx": 5, "pady": 5})
            self._sshchanged()

        def _sshchanged(self):
            ssh = "selected" in self.chkSsh.state()
            if ssh:
                self.txtIdfile.config(state='')
                self.txtPort.config(state='')
                self.txtPath.delete(0, END)
                self.txtPath.insert(0, "root@localhost:"+home+"/some/path"+self.number)
                self.txtPort.delete(0, END)
                self.txtPort.insert(0, "22")
                self.txtIdfile.delete(0, END)
                self.txtIdfile.insert(0, home+"/.ssh/identity")
            else:
                self.txtPort.delete(0, END)
                self.txtIdfile.delete(0, END)
                self.txtPath.delete(0, END)
                self.txtPath.insert(0, home+"/some/path"+self.number)
                self.txtIdfile.config(state='disabled')
                self.txtPort.config(state='disabled')

        def getvalue(self):
            ssh = "selected" in self.chkSsh.state()
            path = self.txtPath.get()
            port = self.txtPort.get()
            idfile = self.txtIdfile.get()
            return ssh, path, port, idfile

        def serialize(self):
            ssh, path, port, idfile = self.getvalue()
            path = path.replace("\\", "/")
            idfile = idfile.replace("\\", "/")
            sssh = "1" if ssh else "0"
            return "#{sssh}\n#{path}\n#{port}\n#{idfile}".format(**locals())

        def deserialize(self, s):
            ssh = s[0][1:] == "1"
            path = s[1][1:]
            port = s[2][1:]
            idfile = s[3][1:]
            self.varSsh.set(ssh)
            self._sshchanged()
            self.txtPath.delete(0, END)
            self.txtPath.insert(0, path)
            self.txtPort.delete(0, END)
            self.txtPort.insert(0, port)
            self.txtIdfile.delete(0, END)
            self.txtIdfile.insert(0, idfile)

    def deserialize(self):
        with open(home + "/.parsley/parsley.cfg", "r") as f:
            lines = [l.strip() for l in f.readlines()]
        sfs1 = []
        sfs2 = []
        i = 0
        for line in lines:
            if i == 0 and line == "#PARSLEY_GUI":
                i = 1
            elif i == 1 and len(sfs1) < 4:
                sfs1.append(line)
                if len(sfs1) == 4:
                    i = 2
            elif i == 2 and len(sfs2) < 4:
                sfs2.append(line)
                if len(sfs2) == 4:
                    break
        self.frameFilesystem1.deserialize(sfs1)
        self.frameFilesystem2.deserialize(sfs2)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack({"fill": "both"})
        self.master.title("parsley")
        self.master.minsize(640, 400)
        self.lblWelcome = Label(self, background="#cdf")
        self.lblWelcome["text"] = "Welcome to parsley. \n" + \
            "Please configure two folders for synchronization and trigger it afterwards."
        self.lblWelcome.pack({"side": "top", "ipadx": 6, "ipady": 6, "anchor": "w", "fill": "x"})
        self.frameFilesystem1 = App.FilesystemFrame(self, "1st Folder")
        self.frameFilesystem1.pack({"side": "top", "fill": "x"})
        self.frameFilesystem2 = App.FilesystemFrame(self, "2nd Folder")
        self.frameFilesystem2.pack({"side": "top", "fill": "x"})
        self.lblStorage = Label(self)
        self.lblStorage["text"] = "The configuration will be stored just before the synchronization starts."
        self.lblStorage.pack({"side": "top", "pady": 10})
        self.buttons = Frame(self)
        self.buttons.pack({"side": "top"})
        self.btnSync = Button(self.buttons)
        self.btnSync["text"] = "Synchronize now"
        self.btnSync["command"] = self._sync
        self.btnSync.pack({"side": "left", "padx": 5, "pady": 5})
        self.btnAdvUsage = Button(self.buttons)
        self.btnAdvUsage["text"] = "Read Me!"
        self.btnAdvUsage["command"] = self._helpadv
        self.btnAdvUsage.pack({"side": "left", "padx": 5, "pady": 5})
        self.output = Frame(self)
        self.output.pack({"side": "top", "padx": 5, "pady": 5, "fill": "both"})
        self.scrollbar = Scrollbar(self.output)
        self.outputtext = Text(self.output)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.outputtext.pack(side=LEFT, expand=True, fill=X)
        self.scrollbar.config(command=self.outputtext.yview)
        self.outputtext.config(yscrollcommand=self.scrollbar.set)
        try:
            self.deserialize()
        except Exception as e:
            print("Error in deserialization: ", e)

    def _sync(self):
        try:
            if not os.path.isdir(home + "/.parsley"):
                os.makedirs(home + "/.parsley")

            ssh, path, port, idfile = self.frameFilesystem1.getvalue()
            isssh = False
            if ssh:
                isssh = True
                fs1 = """SshfsFilesystem(TrashRemove(), sshpath="{path}"
                , idfile="{idfile}", port={port}, name="fs1")"""\
                    .format(path=path, idfile=idfile, port=port)
            else:
                fs1 = """LocalFilesystem(TrashRemove(), path="{path}", name="fs1")""".format(path=path)
                if not os.path.isdir(path+"/.parsley.control"):
                    os.makedirs(path+"/.parsley.control")
            ssh, path, port, idfile = self.frameFilesystem2.getvalue()
            if ssh:
                isssh = True
                fs2 = """SshfsFilesystem(TrashRemove(), sshpath="{path}"
                , idfile="{idfile}", port={port}, name="fs2")"""\
                    .format(path=path, idfile=idfile, port=port)
            else:
                fs2 = """LocalFilesystem(TrashRemove(), path="{path}", name="fs2")""".format(path=path)
                if not os.path.isdir(path+"/.parsley.control"):
                    os.makedirs(path+"/.parsley.control")
            sfs1 = self.frameFilesystem1.serialize()
            sfs2 = self.frameFilesystem2.serialize()
            with open(home + "/.parsley/parsley.cfg", "w") as f:
                f.write("""#   AUTO GENERATED PARSLEY CONFIG FILE
# For advanced usage, you should read the parsley documentation and adapt this
# configuration file to your needs and run parsley via command line.
# If you decide to do so, NEVER use the graphical tool
# again, since it will overwrite your config here.
# A great idea to avoid this danger is to use other names for the config file!

syncs.append(
    InFsSync(
        {fs1},
        {fs2},
        DefaultSync(),
        Logging(logupdate=True, logcreate=True, logremove=True),
        name="sync1",
        interval=timedelta(seconds=0)
))

logging.append(Logger(loggerout=FilestreamLoggerout(),
                formatter=PlaintextLogformat(maxlen=80) , minseverity=Severity.INFO, maxseverity=Severity.ERROR) )

# The following stuff helps the graphical tool to read the configured values
# and can be deleted for command line usage.
#PARSLEY_GUI
{sfs1}
{sfs2}
""".format(**locals()))
            parsleycmd = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/parsley.py"
            if not os.path.isfile(parsleycmd):
                parsleycmd = "parsley"
            if isssh:
                self.outputtext.insert(END, "Note: SSH filesystems need some special care:\n"
                                       + " 1) The target machine must be a known host\n"
                                       + "    (log in at least once via ssh before).\n"
                                       + " 2) The target filesystem must not be completely empty\n"
                                       + "    (create at least a '.parsley.control' folder there).\n\n")
            self.outputtext.insert(END, "Issuing parsley with the following command... Please wait...\n\n")
            self.outputtext.insert(END, ("{parsley} --config {home}/.parsley/parsley.cfg" +
                                   " --datadir {home}/.parsley --sync ALL\n\n")
                                   .format(home=home, parsley=parsleycmd))
            self.outputtext.see(END)
            self.btnSync.config(state='disabled')

            self.done = False
            self.error = None

            def _parsleycallthread():
                try:
                    self.after(100, self._checkdone)
                    r, cmdout = parsley.tools.common.call(parsleycmd, "--config", home+"/.parsley/parsley.cfg",
                                                          "--datadir", home+"/.parsley", "--sync", "ALL")
                    self.outputtext.insert(END, cmdout + "\nThe synchronization ended {succ}.\n---\n\n"
                                           .format(succ="successfully" if (r == 0) else "with errors"))
                    self.outputtext.see(END)
                except Exception as ex:
                    self.error = ex
                self.done = True

            _thread.start_new(_parsleycallthread, ())
        except Exception as e:
            self.outputtext.insert(END, "Internal error: " + str(e) + "\n\n")
            self.outputtext.see(END)

    def _checkdone(self):
        if self.done:
            self.btnSync.config(state='')
            if not self.error is None:
                self.outputtext.insert(END, "Internal error: " + str(self.error) + "\n\n")
                self.outputtext.see(END)

        else:
            self.after(100, self._checkdone)

    def _helpadv(self):
        a = tkinter.messagebox.askyesno("parsley",
                                        "This graphical user interface provides just the basic functionality " +
                                        "of parsley. It creates a configuration file and a runtime directory, " +
                                        "which is required for syncing.\n\nHowever, for advanced usage, you should " +
                                        "modify the config file and use parsley from command line (as the output " +
                                        "in the main window shows). This tool just helps you with the first steps :)" +
                                        "\n\nMaybe you should also check the homepage for news:\n" +
                                        parsley.runtime.projectinformations.homepage +
                                        "\n\nThis is version " + parsley.runtime.projectinformations.version + "." +
                                        "\n\nDo you want to read the complete documentation?")
        if a:
            docfile = self._getdocfile()
            if docfile:
                if sys.platform.startswith('win'):
                    os.startfile(docfile)
                else:
                    subprocess.call(('xdg-open', docfile))
            else:
                tkinter.messagebox.showinfo("parsley",
                                            "Unable to open the documentation :( You should check the homepage.")


    def _getdocfile(self):
        for d in ["/usr/share/doc/parsley", os.path.dirname(sys.argv[0])]:
            if os.path.isfile(d+"/README.pdf"):
                return d+"/README.pdf"


def main():
    myapp = App()
    myapp.mainloop()
