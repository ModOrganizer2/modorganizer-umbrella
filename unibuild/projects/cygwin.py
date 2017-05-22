# Copyright (C) 2015 Sebastian Herbord. All rights reserved.
#
# This file is part of Mod Organizer.
#
# Mod Organizer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mod Organizer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mod Organizer.  If not, see <http://www.gnu.org/licenses/>.


from unibuild import Project
from unibuild.modules import urldownload, build
from config import config
from subprocess import Popen
import os
import logging
import time
import shutil


# installation happens concurrently in separate process. We need to wait for all relevant files to exist,
# and can determine failure only by timeout
timeout = 15   # seconds


def bitness():
    return "64" if config['architecture'] == "x86_64" else "32"

filename = "setup-{}.exe".format(config['architecture'])

url = "http://www.cygwin.com/{}".format(filename)

Cygwin_Mirror = "http://mirrors.kernel.org/sourceware/cygwin/"


def build_func(context):
    proc = Popen([os.path.join(config['paths']['download'], filename),
                   "-q","-C", "Base", "-P", "make,dos2unix,binutils", "-n", "-d", "-O", "-B", "-R", "{}/../cygwin"
                 .format(context['build_path']), "-l", "{}".format(os.path.join(config['paths']['download'])),
                  "-s", "{}".format(Cygwin_Mirror)],env=config['__environment'])
    proc.communicate()
    if proc.returncode != 0:
        logging.error("failed to run installer (returncode %s)",
                      proc.returncode)
        return False
    dos2unix_path = os.path.join(context['build_path'],"../cygwin","bin", "dos2unix.exe")
    make_path = os.path.join(context['build_path'],"../cygwin", "bin", "make.exe")
    wait_counter = timeout
    while wait_counter > 0:
        if os.path.isfile(dos2unix_path) and os.path.isfile(make_path):
            break
        else:
            time.sleep(5.0)
            wait_counter -= 5
    # wait a bit longer because the installer may have been in the process of writing the file
    time.sleep(5.0)

    if wait_counter<=0:
        logging.error("Unpacking of Cygwin timed out");
        return False #We timed out and nothing was installed
    
    return True


cygwin = Project("cygwin")\
    .depend(build.Execute(build_func)
            .depend(urldownload.URLDownload(url))
            )

