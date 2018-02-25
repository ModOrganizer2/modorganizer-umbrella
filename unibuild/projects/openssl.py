# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2018 Mod Organizer contributors.
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


import logging
import os
import shutil
import time
from subprocess import Popen
from glob import glob

from config import config
from unibuild import Project
from unibuild.modules import urldownload, build, Patch

# currently binary installation only
openssl_version = config['openssl_version']

# installation happens concurrently in separate process. We need to wait for all relevant files to exist,
# and can determine failure only by timeout
timeout = 15  # seconds


def bitness():
    return "64" if config['architecture'] == "x86_64" else "32"


filename = "openssl-{}.tar.gz".format(openssl_version)
url = "https://www.openssl.org/source/{}".format(filename)


def openssl_environment():
    result = config['__environment'].copy()
    result['Path'] += ";" + os.path.join(config['paths']['build'], "NASM")
    return result


def openssl_stage(context):
        dest_bin = os.path.join(config["paths"]["install"], "bin")
        dest_lib = os.path.join(config["paths"]["install"], "libs")
        dest_pdb = os.path.join(config["paths"]["install"], "pdb")
        if not os.path.exists(dest_bin):
            os.makedirs(dest_bin)
        if not os.path.exists(dest_lib):
            os.makedirs(dest_lib)
        if not os.path.exists(dest_pdb):
             os.makedirs(dest_pdb)
        for f in glob(os.path.join(config['paths']['build'], "openssl-release", "bin", "ssleay32.dll")):
             shutil.copy(f, os.path.join(dest_bin))
             shutil.copy(f, os.path.join(dest_bin, "dlls"))
        for f in glob(os.path.join(config['paths']['build'], "openssl-release", "bin"
                               , "libeay32.dll")):
             shutil.copy(f, os.path.join(dest_bin))
             shutil.copy(f, os.path.join(dest_bin, "dlls"))
        for f in glob(os.path.join(config['paths']['build'], "openssl-{}".format(openssl_version),"out32dll"
                              , "ssleay32.pdb")):
            shutil.copy(f, os.path.join(dest_pdb))
        for f in glob(os.path.join(config['paths']['build'], "openssl-{}".format(openssl_version),"out32dll"
                              , "libeay32.pdb")):
            shutil.copy(f, os.path.join(dest_pdb))
        for f in glob(os.path.join(config['paths']['build'], "openssl-release", "lib"
                              , "ssleay32.lib")):
            shutil.copy(f, os.path.join(dest_lib, "ssleay32.lib"))
        for f in glob(os.path.join(config['paths']['build'], "openssl-release", "lib"
                              ,"libeay32.lib")):
            shutil.copy(f, os.path.join(dest_lib, "libeay32.lib"))
        return True


OpenSSL_Install = build.Run(r"nmake -f ms\ntdll.mak install",
                      environment=openssl_environment(),
                      name="Install OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))

OpenSSL_Build = build.Run(r"nmake -f ms\ntdll.mak",
                      environment=openssl_environment(),
                      name="Building OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))

OpenSSL_Prep = build.Run(r"ms\do_win64a",
                      environment=openssl_environment(),
                      name="Prepping OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))


Configure_openssl = build.Run(r"{} Configure --openssldir={} --prefix={} VC-WIN{}A".format(config['paths']['perl'],
                                                                                           os.path.join(config['paths']['build'],"openssl-config"),
                                                                                           os.path.join(config['paths']['build'], "openssl-release"),
                                                                                           bitness()),
                      environment=openssl_environment(),
                      name="Configure OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))

openssl = Project("openssl") \
    .depend(build.Execute(openssl_stage)
            .depend(OpenSSL_Install
             .depend(OpenSSL_Build
                .depend(OpenSSL_Prep
                    .depend(Configure_openssl
                        .depend(urldownload.URLDownload(url,tree_depth=1))))))).depend("nasm")