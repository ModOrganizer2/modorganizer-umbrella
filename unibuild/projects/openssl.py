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
    result['Path'] += ";".join([
        os.path.join(config['paths']['build'], "NASM")])
    return result


def openssl_stage(context):
        dest = os.path.join(config["paths"]["install"], "bin")
        if not os.path.exists(dest):
            os.makedirs(dest)
        for f in glob(os.path.join(config['paths']['build'], "openssl-{}"
                              .format(openssl_version), "libssl-*.dll")):
            shutil.copy(f, os.path.join(dest,"libssl.dll"))
        for f in glob(os.path.join(config['paths']['build'], "openssl-{}"
                              .format(openssl_version), "libcrypto-*.dll")):
            shutil.copy(f, os.path.join(dest, "libcrypto.dll"))
        return True


OpenSSL_Test = build.Run(r"nmake test",
                      environment=openssl_environment(),
                      name="Test OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))

OpenSSL_Build = build.Run(r"nmake",
                      environment=openssl_environment(),
                      name="Building OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))


Configure_openssl = build.Run(r"{} Configure --prefix={} VC-WIN{}A".format(config['paths']['perl'],os.path.join(config['paths']['build'], "openssl-release"),bitness()),
                      environment=openssl_environment(),
                      name="Configure OpenSSL",
                      working_directory=lambda: os.path.join(openssl['build_path']))

openssl = Project("openssl") \
    .depend(build.Execute(openssl_stage)
             .depend(OpenSSL_Test
                .depend(OpenSSL_Build
                    .depend(Configure_openssl
                        .depend(urldownload.URLDownload(url,tree_depth=1)))))).depend("nasm")