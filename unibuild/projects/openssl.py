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
from unibuild.modules import urldownload, build, Patch
from config import config
from subprocess import Popen
import os
import logging
import time
import shutil


# currently binary installation only


openssl_version = config['openssl_version']

libeay = "libeay32MD.lib"
ssleay = "ssleay32MD.lib"
# installation happens concurrently in separate process. We need to wait for all relevant files to exist,
# and can determine failure only by timeout
timeout = 15   # seconds


def bitness():
    return "64" if config['architecture'] == "x86_64" else "32"

filename = "Win{}OpenSSL-{}.exe".format(bitness(), openssl_version.replace(".", "_"))

url = "https://slproweb.com/download/{}".format(filename)


def build_func(context):
    proc = Popen([os.path.join(config['paths']['download'], filename),
                  "/VERYSILENT", "/DIR={}".format(context['build_path'])],
                 env=config['__environment'])
    proc.communicate()
    if proc.returncode != 0:
        logging.error("failed to run installer (returncode %s)",
                      proc.returncode)
        return False
    libeay_path = os.path.join(context['build_path'], "lib", "VC", "static", libeay)
    ssleay_path = os.path.join(context['build_path'], "lib", "VC", "static", ssleay)
    wait_counter = timeout
    while wait_counter > 0:
        if os.path.isfile(libeay_path) and os.path.isfile(ssleay_path):
            break
        else:
            time.sleep(1.0)
            wait_counter -= 1
    # wait a bit longer because the installer may have been in the process of writing the file
    time.sleep(1.0)

    if wait_counter<=0:
        logging.error("Unpacking of OpenSSL timed out");
        return False #We timed out and nothing was installed
    
    return True


openssl = Project("openssl") \
    .depend(Patch.Copy([os.path.join(config['paths']['build'], "Win{0}OpenSSL-{1}"
                                     .format("32" if config['architecture'] == 'x86' else "64",
                                             openssl_version.replace(".","_")), "ssleay32.dll"),
                        os.path.join(config['paths']['build'], "Win{0}OpenSSL-{1}"
                                     .format("32" if config['architecture'] == 'x86' else "64",
                                             openssl_version.replace(".", "_")), "libeay32.dll"), ],
                       os.path.join(config["paths"]["install"], "bin","dlls"))
            .depend(build.Execute(build_func)
            .depend(urldownload.URLDownload(url))
            ))

